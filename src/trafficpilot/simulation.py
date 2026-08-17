from __future__ import annotations

from dataclasses import dataclass

from .control import AdaptiveController, FixedTimeController
from .metrics import ControllerMetrics, co2_emissions, fuel_used


@dataclass(frozen=True)
class SimulationParameters:
    duration_seconds: float = 120.0
    time_step_seconds: float = 1.0
    service_rate_vehicles_per_second: float = 1 / 3
    idle_fuel_rate_lps: float = 0.0008
    moving_fuel_rate_lps: float = 0.0012
    co2_kg_per_liter: float = 2.3


def simulate_controller(
    counts: list[int],
    controller: AdaptiveController | FixedTimeController,
    params: SimulationParameters,
) -> ControllerMetrics:
    """Run a deterministic queue-service simulation without opening a GUI window."""
    queues = [int(count) for count in counts]
    initial_total = sum(queues)
    if initial_total == 0:
        return ControllerMetrics()

    current_lane = 0
    time_elapsed = 0.0
    total_wait = 0.0
    total_fuel = 0.0
    queue_samples: list[int] = []
    green_time = 0.0

    while time_elapsed < params.duration_seconds and sum(queues) > 0:
        if isinstance(controller, AdaptiveController):
            order = controller.prioritize_lanes(queues)
            cycle = [(lane, controller.green_time(queues[lane])) for lane in order]
            yellow = controller.yellow_duration
        else:
            cycle = [(lane, controller.green_time()) for lane in range(len(queues))]
            yellow = controller.yellow_duration

        for lane, phase_duration in cycle:
            if time_elapsed >= params.duration_seconds or sum(queues) == 0:
                break
            active_time = min(phase_duration, params.duration_seconds - time_elapsed)
            waiting = sum(queues) - queues[lane]
            total_wait += waiting * active_time
            total_fuel += fuel_used(
                waiting * active_time,
                queues[lane] * active_time,
                params.idle_fuel_rate_lps,
                params.moving_fuel_rate_lps,
            )
            served = min(queues[lane], int(active_time * params.service_rate_vehicles_per_second))
            queues[lane] -= served
            green_time += active_time
            time_elapsed += active_time
            queue_samples.append(sum(queues))
            current_lane = lane

            yellow_time = min(yellow, max(0.0, params.duration_seconds - time_elapsed))
            if yellow_time:
                total_wait += sum(queues) * yellow_time
                total_fuel += fuel_used(
                    sum(queues) * yellow_time,
                    0.0,
                    params.idle_fuel_rate_lps,
                    params.moving_fuel_rate_lps,
                )
                time_elapsed += yellow_time
                queue_samples.append(sum(queues))

    throughput = initial_total - sum(queues)
    avg_wait = total_wait / throughput if throughput else 0.0
    avg_queue = sum(queue_samples) / len(queue_samples) if queue_samples else 0.0
    utilization = green_time / time_elapsed if time_elapsed else 0.0
    _ = current_lane
    return ControllerMetrics(
        total_wait_time=total_wait,
        avg_wait_time=avg_wait,
        fuel_consumption=total_fuel,
        throughput=throughput,
        co2_emissions=co2_emissions(total_fuel, params.co2_kg_per_liter),
        avg_queue_length=avg_queue,
        signal_utilization=utilization,
    )
