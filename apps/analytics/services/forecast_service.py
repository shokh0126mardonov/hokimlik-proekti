import pandas as pd
from prophet import Prophet

from django.db.models.functions import TruncDate
from django.db.models import Count

from apps.applications.models import Application


class ForecastService:

    @staticmethod
    def daily_data():
        qs = (
            Application.objects
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        return list(qs)

    @staticmethod
    def forecast(days: int = 7):
        data = ForecastService.daily_data()

        if len(data) < 10:
            return []

        df = pd.DataFrame(data)
        df.rename(columns={"date": "ds", "count": "y"}, inplace=True)

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)

        result = forecast[["ds", "yhat"]].tail(days)
        return result.to_dict(orient="records")