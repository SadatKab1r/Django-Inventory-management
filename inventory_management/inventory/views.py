from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, InventoryItemForm
from .models import InventoryItem, Category, UserProfile
from inventory_management.settings import LOW_QUANTITY
from django.contrib import messages
from django.http import HttpResponseForbidden


class Index(TemplateView):
    template_name = 'inventory/index.html'


from .models import UserProfile

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        # Get the UserProfile of the logged-in user
        user_profile = UserProfile.objects.get(user=request.user)

        # If the user is an admin, show all items
        if user_profile.role == 'Admin':
            items = InventoryItem.objects.order_by('id')
        else:
            # If the user is not an admin, show only items added by admins
            items = InventoryItem.objects.filter(user__userprofile__role='Admin').order_by('id')

        low_inventory = items.filter(quantity__lte=LOW_QUANTITY)

        if low_inventory.count() > 0:
            message = f"{low_inventory.count()} item{'s' if low_inventory.count() > 1 else ''} have low inventory"
            messages.error(request, message)

        low_inventory_ids = low_inventory.values_list('id', flat=True)

        return render(request, 'inventory/dashboard.html', {
            'items': items,
            'low_inventory_ids': low_inventory_ids
        })


class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )

            login(request, user)
            return redirect('index')

        return render(request, 'inventory/signup.html', {'form': form})


class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'Admin':
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'Admin':
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)


class DeleteItem(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/delete_item.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'item'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'Admin':
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)
