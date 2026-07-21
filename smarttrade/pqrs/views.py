# pqrs/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PQRSForm

def formulario_pqrs(request):
    if request.method == 'POST':
        form = PQRSForm(request.POST)
        if form.is_valid():
            pqrs = form.save()
            print("✅ PQRS guardada correctamente:", pqrs.nombre, pqrs.correo)
            messages.success(request, "Gracias por comunicarte con nosotros. Pronto te daremos respuesta. Te llegará al correo electrónico máximo en 3 días hábiles.")
            return redirect('pqrs:pqrs_exito')
        else:
            print("❌ Errores en el formulario:", form.errors)
            messages.error(request, "Ocurrió un error. Verifica los datos ingresados.")
    else:
        form = PQRSForm()

    return render(request, 'pqrs/formulario.html', {'form': form})


def pqrs_exito(request):
    return render(request, 'pqrs/exito.html')