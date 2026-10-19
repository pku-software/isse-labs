"""本地监控实验访问调度器（Python 3.9+，仅使用标准库）。

先由 Agent 补齐同目录 project_adapter.py，再运行本文件。
它只通过 HTTP 访问应用，不直接读写 Prometheus 指标。
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

import project_adapter


@dataclass(frozen=True)
class Phase:
    name: str
    rate: float
    delay: float
    error_every: int = 0


@dataclass(frozen=True)
class Observation:
    success: bool
    transport_error: bool
    expected_error: bool
    seconds: float


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def local_origin(url):
    """只允许访问本机；也用于检查适配器构造的请求是否偏离目标。"""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError("目标必须为本地 http/https 地址")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("地址不得包含凭据、查询参数或片段")
    host = parts.hostname.lower()
    if host != "localhost":
        try:
            is_local = ipaddress.ip_address(host).is_loopback
        except ValueError:
            is_local = False
        if not is_local:
            raise ValueError("本实验仅访问 localhost、127.0.0.1 或 ::1")
    return parts.scheme, host, parts.port or (443 if parts.scheme == "https" else 80)


def send_one(base_url, phase, number, timeout, stop):
    if stop.is_set():
        return None
    expected_error = bool(phase.error_every and number % phase.error_every == 0)
    request = project_adapter.build_chat_request(
        base_url, "监控实验测试消息", phase.delay, expected_error
    )
    if local_origin(request.full_url) != local_origin(base_url):
        raise ValueError("适配器请求必须与 --base-url 使用同一主机和端口")
    started = time.monotonic()
    try:
        # 每个线程独立 opener；禁止重定向至其他服务。
        opener = build_opener(ProxyHandler({}), NoRedirect())
        try:
            with opener.open(request, timeout=timeout) as response:
                code = response.status
                body = response.read(1024 * 1024)
        except HTTPError as error:
            with error:
                code = error.code
                body = error.read(1024 * 1024)
        success = project_adapter.response_is_success(code, body)
        if not isinstance(success, bool):
            raise TypeError("response_is_success 必须返回 bool")
        return Observation(success, False, expected_error, time.monotonic() - started)
    except (URLError, TimeoutError, OSError):
        return Observation(False, True, expected_error, time.monotonic() - started)


def run_phase(base_url, phase, duration, concurrency, timeout, stop):
    """固定发送间隔、有限并发，不堆积无界请求队列。阶段结束等待在途请求。"""
    start_time = timestamp()
    started = time.monotonic()
    pending, observations = set(), []
    scheduled = skipped = 0

    def collect_done():
        for future in list(pending):
            if future.done():
                pending.remove(future)
                result = future.result()
                if result is not None:
                    observations.append(result)

    print(f"[{start_time}] {phase.name}: {duration:g}s, "
          f"目标 {phase.rate:g} 次/秒, 后端延迟 {phase.delay:g}s", flush=True)
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        try:
            next_send = started
            while not stop.is_set() and time.monotonic() < started + duration:
                collect_done()
                now = time.monotonic()
                if now < next_send:
                    stop.wait(min(next_send - now, 0.05))
                    continue
                scheduled += 1
                if len(pending) < concurrency:
                    pending.add(pool.submit(send_one, base_url, phase, scheduled, timeout, stop))
                else:
                    skipped += 1
                # 调度落后时不突发补发；实际发送量写入结果。
                next_send = max(next_send + 1 / phase.rate, now)
            for future in pending:
                result = future.result()
                if result is not None:
                    observations.append(result)
        except BaseException:
            stop.set()
            for future in pending:
                future.cancel()
            raise

    durations = [item.seconds for item in observations]
    report = {
        "phase": phase.name, "started_at": start_time, "ended_at": timestamp(),
        "settings": asdict(phase), "duration_seconds": duration,
        "scheduled": scheduled, "sent": len(observations), "skipped": skipped,
        "success": sum(item.success for item in observations),
        "http_or_business_errors": sum(not item.success and not item.transport_error
                                       for item in observations),
        "transport_errors": sum(item.transport_error for item in observations),
        "unexpected_results": sum(not item.transport_error and
                                  item.success == item.expected_error
                                  for item in observations),
        # 客户端耗时含网络开销，不等同于服务端 Histogram。
        "client_mean_seconds": sum(durations) / len(durations) if durations else None,
    }
    print(f"[{report['ended_at']}] {phase.name} 完成: 发送 {report['sent']}, "
          f"成功 {report['success']}, 业务/HTTP错误 {report['http_or_business_errors']}, "
          f"网络错误 {report['transport_errors']}, 非预期结果 {report['unexpected_results']}, "
          f"跳过 {skipped}", flush=True)
    return report


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:5001")
    parser.add_argument("--scenario", choices=["all", "baseline", "burst", "slow", "errors", "recovery"], default="all")
    parser.add_argument("--phase-seconds", type=float, default=30)
    parser.add_argument("--baseline-rate", type=float, default=1)
    parser.add_argument("--burst-rate", type=float, default=4)
    parser.add_argument("--slow-rate", type=float, default=2)
    parser.add_argument("--slow-delay", type=float, default=3)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--error-every", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--settle-seconds", type=float, default=10)
    parser.add_argument("--output", default="simulation_results.json")
    args = parser.parse_args(argv)
    try:
        local_origin(args.base_url)
        if urlsplit(args.base_url).path not in ("", "/"):
            raise ValueError("--base-url 只写服务根地址，接口路径由适配器填写")
        for name in ("phase_seconds", "baseline_rate", "burst_rate", "slow_rate", "timeout"):
            value = getattr(args, name)
            if not 0 < value <= (300 if name == "phase_seconds" else 30):
                raise ValueError(f"{name} 超出教学实验范围")
        if not 1 <= args.concurrency <= 20 or args.error_every < 2:
            raise ValueError("并发数应为 1～20，error-every 至少为 2")
        if not 0.1 < args.timeout or not 0 <= args.slow_delay < args.timeout or not 0 <= args.settle_seconds <= 60:
            raise ValueError("请求超时应大于 0.1 秒及模拟延迟；收尾等待为 0～60 秒")
    except ValueError as error:
        parser.error(str(error))
    return args


def main(argv=None):
    args = arguments(argv)
    if project_adapter.ADAPTER_READY is not True:
        print("适配尚未完成：请让 Agent 补齐 project_adapter.py，再运行脚本。")
        return 2
    stop = threading.Event()
    phases = [
        Phase("baseline", args.baseline_rate, 0.1),
        Phase("burst", args.burst_rate, 0.1),
        Phase("slow", args.slow_rate, args.slow_delay),
        Phase("errors", args.baseline_rate, 0.1, args.error_every),
        Phase("recovery", args.baseline_rate, 0.1),
    ]
    reports = []
    interrupted = False
    try:
        if project_adapter.confirm_mock_mode(args.base_url.rstrip("/"), args.timeout) is not True:
            raise ValueError("服务未确认处于 mock 模式，未发送聊天请求")
        print("已核验服务模拟模式；脚本通过实际 HTTP 接口产生监测数据。", flush=True)
        for phase in phases:
            if args.scenario in ("all", phase.name):
                reports.append(run_phase(args.base_url.rstrip("/"), phase, args.phase_seconds,
                                         args.concurrency, args.timeout, stop))
        print(f"请求已结束，等待 {args.settle_seconds:g}s 让采集器记录恢复状态。", flush=True)
        stop.wait(args.settle_seconds)
    except KeyboardInterrupt:
        stop.set()
        interrupted = True
        print("已中断，停止发出新请求；结果只保留已完成的阶段。", flush=True)
    except Exception as error:
        print(f"运行失败（{type(error).__name__}）：请检查适配器、模拟模式及本地服务。")
        return 2
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"base_url": args.base_url, "interrupted": interrupted,
                                 "phases": reports}, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"阶段时间与结果已写入 {output}；请与 Grafana 曲线对照。", flush=True)
    if interrupted:
        return 130
    return int(any(item["transport_errors"] or item["unexpected_results"] for item in reports))


if __name__ == "__main__":
    raise SystemExit(main())
