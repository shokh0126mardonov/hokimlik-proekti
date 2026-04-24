# apps/analytics/services/ai_service.py

class AIService:

    @staticmethod
    def _to_seconds(td):
        return td.total_seconds() if td else 0

    @staticmethod
    def generate_insight(metrics, by_service, sla):
        if len(by_service) < 2:
            return "Ma'lumot yetarli emas."

        worst = max(by_service, key=lambda x: AIService._to_seconds(x["avg_time"]))
        best = min(by_service, key=lambda x: AIService._to_seconds(x["avg_time"]))

        diff_hours = int(
            (worst["avg_time"] - best["avg_time"]).total_seconds() / 3600
        )

        insight = (
            f"{worst['service__name']} xizmatida ishlov berish vaqti "
            f"{best['service__name']} ga nisbatan {diff_hours} soatga sekinroq. "
        )

        if metrics["avg_execution_time"]:
            insight += "Asosiy kechikish mahalla bosqichida. "

        if sla["rate"] > 0:
            insight += f"SLA buzilish darajasi {sla['rate']*100:.1f}%."

        return insight