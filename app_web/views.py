from django.shortcuts import render

# Create your views here.
from django.views import View

import json


class AppIndex(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(AppIndex, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/index.html')
