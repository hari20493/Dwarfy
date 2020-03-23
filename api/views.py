from datetime import datetime

import pytz
from django.db.models import F, Count
from django.db.models.functions import TruncHour, TruncDay, TruncSecond, ExtractDay, ExtractHour, TruncMonth, \
    ExtractMonth
from django.utils.decorators import method_decorator

# Create your views here.
from .utils import *
from .models import *


class shortner(ApiView):
    @method_decorator(get_raw_data)
    def post(self, request):
        dict = {}
        url_to_be_shortened = request.DATA.get('url', '')
        title = request.DATA.get('title', '')
        if url_to_be_shortened:
            urls_obj, created = Urls.objects.get_or_create(long_url=url_to_be_shortened)
            urls_obj.title = title
            urls_obj.save()
            if created:
                reports_obj = Reports.objects.create(url=urls_obj)
                self.flag = StatusCode.HTTP_200_OK
                dict['message'] = "Url Shortened"
            else:
                self.flag = StatusCode.HTTP_400_BAD_REQUEST
                dict['message'] = "Url Already Exists. Please try again with another URL"

        else:
            self.flag = StatusCode.HTTP_400_BAD_REQUEST
            dict['message'] = "Url cannot be empty. Please fill in the Url that you need to be shortened"

        return JsonWrapper(dict, self.flag)

    def get(self, request):
        dict = {}
        url_obj = Reports.objects.all().annotate(long_url=F('url__long_url'), slug=F('url__slug')).values()
        dict['data'] = (list(url_obj))

        self.flag = StatusCode.HTTP_200_OK
        return JsonWrapper(dict, self.flag)


class Report(ApiView):
    def get(self, *args, **kwargs):
        print(kwargs['slug'])
        dict = {}
        hits_per_hour = Logs.objects \
            .filter(url__slug=kwargs['slug']) \
            .annotate(hour=TruncHour('hit_time', tzinfo=pytz.timezone('Asia/Kolkata'))) \
            .values('hour') \
            .annotate(events=Count('url__long_url')) \
            .order_by('hour').annotate(time=ExtractHour('hit_time', tzinfo=pytz.timezone('Asia/Kolkata'))).filter(
            hit_time__date=datetime.date(datetime.now()))
        hits_per_day = Logs.objects \
            .filter(url__slug=kwargs['slug']) \
            .annotate(day=TruncDay('hit_time')) \
            .values('day') \
            .annotate(events=Count('url__long_url')) \
            .order_by('day').annotate(days=ExtractDay('hit_time'))
        hits_per_month = Logs.objects \
            .filter(url__slug=kwargs['slug']) \
            .annotate(month=TruncMonth('hit_time')) \
            .values('month') \
            .annotate(events=Count('url__long_url')) \
            .order_by('month').annotate(months=ExtractMonth('hit_time'))
        dict["data"] = {
            'hits_per_hour': list(hits_per_hour),
            'hits_per_day': list(hits_per_day),
            'hits_per_month': list(hits_per_month),
            "day":datetime.date(datetime.now())

        }
        self.flag = StatusCode.HTTP_200_OK
        return JsonWrapper(dict, self.flag)


def search(self):
    try:
        search_slug = self.GET.get('query', '')
        dict = {}
        if search_slug:
            url_objects = Reports.objects.filter(url__title__icontains=search_slug).annotate(
                long_url=F('url__long_url'), title=F('url__title'),slug=F('url__slug')).values()
            dict['data'] = (list(url_objects))

        else:
            dict['data'] = []
            dict['message'] = "No matching title exists in our list"
        self.flag = StatusCode.HTTP_200_OK
    except Exception as e:
        dict['data'] = str(e)
        self.flag = StatusCode.HTTP_500_INTERNAL_SERVER_ERROR
    return JsonWrapper(dict, self.flag)
