from collections import deque

from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class Menu(View):
    template_name = 'menu.html'

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)


class Queue:
    line = {'change_oil': [], 'inflate_tires': [], 'diagnostic': []}
    q = []

    def insert(self, service, number):
        self.line[service].append(number)

    def values(self):
        for service_line in self.line.values():
            for number in service_line:
                yield number

    def queue(self):
        for service_line in self.line.values():
            for number in service_line:
                self.q.append(number)
        return self.q

    def remove(self):
        line = ''
        for service_line in self.line.keys():
            if self.line[service_line]:
                self.line[service_line].pop(0)
                line = service_line
                break
        return line


class ServicePage(View):
    template_name = "service_page.html"
    line_of_cars = {'change_oil': 0, 'inflate_tires': 0, 'diagnostic': 0, 'count': 0}
    tickets = Queue()
    oil_change_waiting_time = 0
    tires_waiting_time = 0
    diagnostic_waiting_time = 0
    context = {}

    def get(self, request, *args, **kwargs):
        line = kwargs['page']
        self.line_of_cars['count'] += 1
        time_to_wait = self.calculate_time_to_wait()
        self.tickets.insert(line, self.line_of_cars['count'])
        self.line_of_cars[line] += 1
        self.context = {"number": self.line_of_cars['count'], "minutes_to_wait": time_to_wait[line]}
        return render(request, self.template_name, context=self.context)

    def calculate_time_to_wait(self):
        self.oil_change_waiting_time = self.line_of_cars['change_oil'] * 2
        self.tires_waiting_time = self.line_of_cars['inflate_tires'] * 5 + self.oil_change_waiting_time
        self.diagnostic_waiting_time = self.line_of_cars['diagnostic'] * 30 + self.tires_waiting_time

        return {
            'change_oil': self.oil_change_waiting_time,
            'inflate_tires': self.tires_waiting_time,
            'diagnostic': self.diagnostic_waiting_time
        }


class OperatorMenu(ServicePage):
    template_name = "operator_menu.html"

    def get(self, request, *args, **kwargs):
        context = self.line_of_cars
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if self.line_of_cars['count'] > 0:
            self.tickets.q = [next(self.tickets.values())]
            line = self.tickets.remove()
            if self.line_of_cars[line] > 0:
                self.line_of_cars[line] -= 1
        return render(request, self.template_name, context=self.line_of_cars)


class Next(View):
    template_name = "next.html"
    tickets = ServicePage.tickets

    def get(self, request, *args, **kwargs):
        next_ticket = self.get_next_ticket()
        if next_ticket:
            return HttpResponse(f"<div>Next ticket #{next_ticket}</div>")
        else:
            return HttpResponse("<div>Waiting for the next client</div>")

    def get_next_ticket(self):
        q = self.tickets.q
        return q[0] if q else None
