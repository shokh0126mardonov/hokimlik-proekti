class InsightService:

    @staticmethod
    def oqsoqol_insight(stats: dict) -> str:
        total = stats.get("total", 0)
        pending = stats.get("pending", 0)
        closed = stats.get("closed", 0)

        if total == 0:
            return "Hozircha arizalar mavjud emas"

        ratio = pending / total

        if ratio > 0.5:
            return "Kutilayotgan arizalar ko‘p — yuklama oshgan"

        if closed > pending:
            return "Oqsoqol samarali ishlamoqda"

        return "Holat barqaror"

    @staticmethod
    def bottleneck_insight(data: dict) -> str:
        review = data.get("avg_review_time")
        closing = data.get("avg_closing_time")

        if review and closing:
            if closing > review:
                return "Mahalla bosqichida kechikish mavjud"
            else:
                return "Hokim bosqichi sekin ishlamoqda"

        return "Yetarli data yo‘q"