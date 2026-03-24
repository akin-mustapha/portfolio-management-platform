from datetime import date, timedelta

from .domain.entities import RebalanceConfig, RebalancePlan


def generate_plan(
    configs: list[RebalanceConfig],
    current_weights: dict[str, float],
) -> RebalancePlan | None:
    """Pure function — no DB access. Fully testable in isolation.

    Args:
        configs: Active rebalance configs loaded from portfolio.rebalance_config.
        current_weights: {ticker: position_weight_pct} from analytics.fact_valuation.

    Returns:
        RebalancePlan if any asset is outside its threshold, else None.
    """
    actions = []

    for config in configs:
        if not config.is_active:
            continue

        actual = current_weights.get(config.ticker, 0.0)
        drift = actual - config.target_weight_pct

        if abs(drift) <= config.rebalance_threshold_pct:
            continue

        action = "reduce" if drift > 0 else "increase"
        if config.correction_days <= 0:
            continue
        daily_correction = drift / config.correction_days

        daily_steps = []
        for day in range(1, config.correction_days + 1):
            step_date = (date.today() + timedelta(days=day)).isoformat()
            step_target = round(actual - daily_correction * day, 2)
            daily_steps.append({
                "date": step_date,
                "target_weight_pct": step_target,
            })

        actions.append({
            "ticker": config.ticker,
            "current_weight_pct": round(actual, 2),
            "target_weight_pct": config.target_weight_pct,
            "drift_pct": round(drift, 2),
            "action": action,
            "daily_steps": daily_steps,
        })

    if not actions:
        return None

    max_days = max(len(a["daily_steps"]) for a in actions)
    completion_date = (date.today() + timedelta(days=max_days)).isoformat()
    total_drift = round(sum(abs(a["drift_pct"]) for a in actions), 2)
    n = len(actions)

    plan_json = {
        "summary": f"{n} asset{'s' if n > 1 else ''} outside threshold — correction over {max_days} day{'s' if max_days > 1 else ''}",
        "total_drift_pct": total_drift,
        "actions": actions,
    }

    return RebalancePlan(
        id=None,
        created_date=date.today().isoformat(),
        target_completion_date=completion_date,
        status="draft",
        plan_json=plan_json,
        email_sent=False,
    )
