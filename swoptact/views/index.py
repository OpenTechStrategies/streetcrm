# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from django.core import urlresolvers
from django.views import generic
from django.contrib import auth
from django.contrib.auth import forms, decorators
from django.utils.decorators import method_decorator

class LoginView(generic.FormView):
	""" Handles logging in a user to the site """

	template_name = "index.html"
	form_class = forms.AuthenticationForm
	model = auth.get_user_model()

	def form_valid(self, form, *args, **kwargs):
		auth.login(self.request, form.get_user())
		return super(LoginView, self).form_valid(form, *args, **kwargs)

	def get_success_url(self, *args, **kwargs):
		return urlresolvers.reverse_lazy("success")


class SuccessView(generic.TemplateView):
	""" Simple view to show successful login """
	template_name = "success.html"

	@method_decorator(decorators.login_required)
	def dispatch(self, *args, **kwargs):
		return super(SuccessView, self).dispatch(*args, **kwargs)