from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Plan, PQRS
from .forms import RegistroForm
from .models import Perfil
from django.contrib import messages

import os
import csv
from django.conf import settings

import json
from statistics import mean, pstdev
from math import sqrt


def _ensure_perfil(user):
    """Obtener o crear el Perfil asociado a un usuario.

    Devuelve la instancia Perfil (nunca None). Crear un perfil vacío si no existe.
    """
    perfil, _ = Perfil.objects.get_or_create(user=user)
    return perfil


def _load_latest_predictions():
    """Lee el archivo CSV de predicciones y devuelve un dict con pred_next_day y pred_next_week.

    Ruta esperada: <BASE_DIR>/usuarios/static/data/predicciones_finales.csv
    Devuelve cadenas formateadas con 2 decimales, o 'N/A' en caso de error.
    """
    csv_path = os.path.join(settings.BASE_DIR, 'usuarios', 'static', 'data', 'predicciones_finales.csv')
    if not os.path.exists(csv_path):
        return {"pred_next_day": "N/A", "pred_next_week": "N/A"}

    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return {"pred_next_day": "N/A", "pred_next_week": "N/A"}
            last = rows[-1]
            # Intentar convertir a float y formatear
            pred_day = last.get('pred_next_day') or last.get('pred_next_day'.lower())
            pred_week = last.get('pred_next_week') or last.get('pred_next_week'.lower())

            try:
                pred_day_val = float(pred_day)
                pred_day_str = f"{pred_day_val:,.2f}"
            except Exception:
                pred_day_str = str(pred_day) if pred_day not in (None, '') else "N/A"

            try:
                pred_week_val = float(pred_week)
                pred_week_str = f"{pred_week_val:,.2f}"
            except Exception:
                pred_week_str = str(pred_week) if pred_week not in (None, '') else "N/A"

            return {"pred_next_day": pred_day_str, "pred_next_week": pred_week_str}
    except Exception:
        return {"pred_next_day": "N/A", "pred_next_week": "N/A"}


#pagina index
@login_required
def home(request):
    preds = _load_latest_predictions()
    return render(request, "usuarios/index.html", preds)

#pagina login
def login_view(request):
    if request.method == "POST":
        username=request.POST["usuario"]
        password=request.POST["contraseña"]
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name="asesores").exists():
                return redirect("panel_asesores")  # nombre de la URL del panel de asesores
            else:
                return redirect("home")  # página normal de usuarios
        else:
            return render(request, "usuarios/login.html", {"error": "Usuario o contraseña incorrectos"})
    return render(request, "usuarios/login.html")

#funcion logout
def logout_view(request):
    logout(request)
    return redirect("login")

#pagina elegir planes
def planes_view(request):
    planes = Plan.objects.all()

    # Convertimos beneficios en lista
    for plan in planes:
        plan.beneficios_lista = plan.beneficios.split(",")

    return render(request, "usuarios/planes.html", {"planes": planes})

#pagina registro
def registro(request):
    plan_seleccionado = request.GET.get('plan', None)

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            phone = form.cleaned_data['phone']
            plan_nombre = form.cleaned_data['plan'] or plan_seleccionado

            # Buscar el objeto Plan en la base de datos
            plan = Plan.objects.get(nombre__iexact=plan_nombre)

            # Crear perfil
            Perfil.objects.create(user=user, phone=phone, plan=plan)

            return redirect('login')
    else:
        form = RegistroForm(initial={'plan': plan_seleccionado})

    return render(request, 'usuarios/registro.html', {'form': form})

# ----------------------------
# PQRS
# ----------------------------
@login_required
def pqrs_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        mensaje = request.POST.get('mensaje')
        
        if nombre and correo and mensaje:
            PQRS.objects.create(
                usuario=request.user,
                nombre=nombre,
                correo=correo,
                mensaje=mensaje
            )
            messages.success(request, "Tu PQRS ha sido enviada correctamente. Te responderemos pronto.")
            return redirect('pqrs')
        else:
            messages.error(request, "Por favor completa todos los campos.")
    
    # Mostrar PQRs anteriores del usuario
    pqrs_list = PQRS.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, "usuarios/pqrs.html", {'pqrs_list': pqrs_list})


# ----------------------------
# REPORTES
# ----------------------------
@login_required
def reportes_view(request):
    """Genera datos y gráficos básicos/avanzados según el plan del usuario.

    - Busca CSV en usuarios/static/data/predicciones_finales.csv con columnas: date, close, volume, pred_next_day, pred_next_week
    - Calcula métricas básicas (variación %, volatilidad, predicción corta) y extras según plan.
    """
    perfil = _ensure_perfil(request.user)
    plan_nombre = (perfil.plan.nombre if perfil.plan else 'Sin plan')

    # Ruta al archivo de datos históricos
    hist_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'data', 'Ecopetrol_unificado_limpio.csv')
    # Ruta al archivo de predicciones
    pred_path = os.path.join(settings.BASE_DIR, 'usuarios', 'static', 'data', 'predicciones_finales.csv')

    dates = []
    closes = []
    volumes = []
    pred_next_day = None
    pred_next_week = None

    # Leer datos históricos
    if os.path.exists(hist_path):
        try:
            with open(hist_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    # Leer de forma defensiva
                    date = row.get('Fecha')
                    close = row.get('Precio cierre')
                    vol = row.get('Volumen')
                    if close is None:
                        continue
                    try:
                        close_v = float(close)
                    except Exception:
                        continue
                    dates.append(date)
                    closes.append(close_v)
                    try:
                        volumes.append(float(vol) if vol not in (None, '') else 0.0)
                    except Exception:
                        volumes.append(0.0)
        except Exception as e:
            # En caso de fallo leyendo el CSV histórico no queremos que la vista colapse
            print(f"Error leyendo datos históricos: {e}")

    # Leer predicciones
    if os.path.exists(pred_path):
        try:
            with open(pred_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pd = row.get('pred_next_day')
                    pw = row.get('pred_next_week')
                    if pd:
                        try:
                            pred_next_day = float(pd)
                        except Exception:
                            pred_next_day = None
                    if pw:
                        try:
                            pred_next_week = float(pw)
                        except Exception:
                            pred_next_week = None
        except Exception:
            # lectura fallida
            dates, closes, volumes = [], [], []

    # limitar series para mostrar (últimos 90 registros por ejemplo)
    MAX_POINTS = 90
    if len(closes) > MAX_POINTS:
        dates = dates[-MAX_POINTS:]
        closes = closes[-MAX_POINTS:]
        volumes = volumes[-MAX_POINTS:]

    # métricas básicas
    pct_changes = []
    returns = []
    for i in range(1, len(closes)):
        prev = closes[i-1]
        curr = closes[i]
        if prev != 0:
            pct = (curr - prev) / prev * 100.0
            pct_changes.append(pct)
            returns.append((curr - prev) / prev)

    volatility = None
    if returns:
        try:
            volatility = pstdev(returns) * sqrt(252)  # anualizada (si series diarias)
        except Exception:
            volatility = None

    # Riesgo estimado (Premium y Oro): probabilidad de pérdida/ganancia basada en los retornos históricos
    riesgo_prob_perdida = None
    riesgo_prob_ganancia = None
    var_95 = None
    es_95 = None
    if plan_nombre.lower() in ('premium', 'oro') and returns:
        try:
            # Usar ventana reciente para estimar probabilidad (máx 60 días o todos si menos)
            window = min(60, len(returns))
            recent = returns[-window:]
            n = len(recent)
            if n > 0:
                losses = sum(1 for r in recent if r < 0)
                riesgo_prob_perdida = losses / n
                riesgo_prob_ganancia = 1.0 - riesgo_prob_perdida

                # Para plan Oro, calcular VaR(95%) y Expected Shortfall (promedio de pérdidas por debajo del VaR)
                if plan_nombre.lower() == 'oro':
                    sorted_ret = sorted(recent)
                    idx = max(0, int(0.05 * n) - 1)
                    # VaR95 como pérdida típica (valor negativo), convertir a positivo para presentación
                    var_95 = -sorted_ret[idx] if idx < len(sorted_ret) else None
                    # Expected Shortfall (ES) promedio de peores 5%
                    tail = [r for r in sorted_ret if r <= sorted_ret[idx]] if n > 0 else []
                    if tail:
                        es_95 = - (sum(tail) / len(tail))
                    else:
                        es_95 = None
        except Exception as e:
            print(f"Error calculando riesgo estimado: {e}")

    # Predicción corta: preferir pred_next_day del CSV, si no estimar AR(1)
    pred_short = pred_next_day
    if pred_short is None and len(closes) >= 2:
        # simple extrapolación por último cambio
        pred_short = closes[-1] + (closes[-1] - closes[-2])

    # Resumen semanal (últimos 7 vs prev 7)
    resumen_semanal = None
    if len(closes) >= 14:
        last7 = mean(closes[-7:])
        prev7 = mean(closes[-14:-7])
        delta = ((last7 - prev7) / prev7 * 100.0) if prev7 != 0 else None
        resumen_semanal = {'last7': last7, 'prev7': prev7, 'delta_pct': delta}

    # Comentario automático: solo para plan Oro (más completo)
    comentario_simple = None
    if plan_nombre.lower() == 'oro' and len(closes) >= 7:
        try:
            ma7 = mean(closes[-7:])
            last = closes[-1]
            pct_to_ma = (last - ma7) / ma7 * 100 if ma7 != 0 else 0
            if pct_to_ma > 2:
                comentario_simple = 'Fuertemente alcista: encima de la media móvil 7 días.'
            elif pct_to_ma > 0:
                comentario_simple = 'Moderadamente alcista: ligeramente por encima de la media móvil 7 días.'
            elif pct_to_ma > -2:
                comentario_simple = 'Lateral con ligera presión a la baja.'
            else:
                comentario_simple = 'Tendencia bajista: por debajo de la media móvil 7 días.'
            # Añadir mención de riesgo si está disponible
            if riesgo_prob_perdida is not None:
                rp_pct = round(riesgo_prob_perdida * 100, 1)
                comentario_simple += f" Riesgo estimado de pérdida diaria ~{rp_pct}% (basado en últimos {min(60, len(returns))} días)."
        except Exception as e:
            print(f"Error generando comentario para Oro: {e}")

    # Extras para premium
    sma7 = sma21 = rsi14 = macd = macd_signal = macd_hist = boll_upper = boll_lower = None
    pred_medium = pred_next_week
    if plan_nombre.lower() in ('premium', 'oro'):
        # medias móviles simples
        def simple_sma(series, n):
            if len(series) < n:
                return None
            return [None]*(n-1) + [mean(series[i-n+1:i+1]) for i in range(n-1, len(series))]

        if len(closes) >= 7:
            sma7 = simple_sma(closes, 7)
        if len(closes) >= 21:
            sma21 = simple_sma(closes, 21)

        # RSI simple (14)
        def compute_rsi(series, period=14):
            if len(series) < period+1:
                return None
            gains = []
            losses = []
            for i in range(1, len(series)):
                diff = series[i] - series[i-1]
                gains.append(max(diff, 0))
                losses.append(abs(min(diff, 0)))
            avg_gain = mean(gains[-period:])
            avg_loss = mean(losses[-period:])
            if avg_loss == 0:
                return 100.0
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))

        rsi14 = compute_rsi(closes, 14) if len(closes) >= 15 else None

        # MACD simple
        def ema(series, period):
            if len(series) < period:
                return None
            k = 2/(period+1)
            ema_vals = [mean(series[:period])]
            for price in series[period:]:
                ema_vals.append((price - ema_vals[-1]) * k + ema_vals[-1])
            # pad
            return [None]*(period-1) + ema_vals

        ema12 = ema(closes, 12)
        ema26 = ema(closes, 26)
        if ema12 and ema26:
            macd = [ (a - b) if (a is not None and b is not None) else None for a,b in zip(ema12, ema26) ]
            # signal as 9-period EMA of macd (filter Nones)
            macd_vals = [v for v in macd if v is not None]
            sig = None
            if len(macd_vals) >= 9:
                sig_series = ema(macd_vals, 9)
                if sig_series:
                    macd_signal = sig_series[-1]
                    macd_hist = macd_vals[-1] - macd_signal

        # Bollinger Bands (20, 2)
        if len(closes) >= 20:
            window = 20
            ma20 = [mean(closes[i-window+1:i+1]) for i in range(window-1, len(closes))]
            stds = []
            for i in range(window-1, len(closes)):
                slice_ = closes[i-window+1:i+1]
                try:
                    s = pstdev(slice_)
                except Exception:
                    s = 0.0
                stds.append(s)
            boll_upper = [m + 2*s for m,s in zip(ma20, stds)]
            boll_lower = [m - 2*s for m,s in zip(ma20, stds)]

    # Extras para oro (simulaciones y explicaciones)
    escenarios = None
    importancia_variables = None
    if plan_nombre.lower() == 'oro':
        # simulación simple: variación del 5% en Brent -> impacto proporcional calculado por correlación si hay external data
        externos_path = os.path.join(settings.BASE_DIR, 'usuarios', 'static', 'data', 'externals.csv')
        if os.path.exists(externos_path):
            try:
                brent = []
                for row in csv.DictReader(open(externos_path, newline='', encoding='utf-8')):
                    try:
                        brent.append(float(row.get('brent') or row.get('Brent') or 0))
                    except Exception:
                        brent.append(0.0)
                # correlación simple
                if len(brent) == len(closes) and len(brent) > 1:
                    # compute simple covariance-based correlation
                    avg_b = mean(brent)
                    avg_c = mean(closes)
                    num = sum((b-avg_b)*(c-avg_c) for b,c in zip(brent, closes))
                    den = (sum((b-avg_b)**2 for b in brent)**0.5) * (sum((c-avg_c)**2 for c in closes)**0.5)
                    corr = (num/den) if den != 0 else 0
                else:
                    corr = 0.5
            except Exception:
                corr = 0.5
        else:
            corr = 0.5

        # escenarios: impacto de +/-5% en Brent
        if closes:
            base = closes[-1]
            escenarios = {
                'brent_plus5': base * (1 + 0.05 * corr),
                'brent_minus5': base * (1 - 0.05 * corr),
            }
        importancia_variables = {'Brent': 0.4, 'USD/COP': 0.25, 'EMBI': 0.15, 'Produccion': 0.2}

    context = {
        'plan': plan_nombre,
        'dates': json.dumps(dates),
        'closes': json.dumps(closes),
        'volumes': json.dumps(volumes),
        'pct_changes': json.dumps(pct_changes),
        'volatility': volatility,
        'pred_short': pred_short,
        'pred_medium': pred_medium,
        'resumen_semanal': resumen_semanal,
        'comentario_simple': comentario_simple,
        'sma7': json.dumps(sma7) if sma7 is not None else None,
        'sma21': json.dumps(sma21) if sma21 is not None else None,
        'rsi14': rsi14,
        'macd_hist': macd_hist,
        'boll_upper': json.dumps(boll_upper) if boll_upper is not None else None,
        'boll_lower': json.dumps(boll_lower) if boll_lower is not None else None,
        'escenarios': escenarios,
        'importancia_variables': importancia_variables,
    }

    return render(request, 'usuarios/reportes.html', context)

# ----------------------------
# PÁGINA PRINCIPAL (INDEX)
# ----------------------------
@login_required
def index_view(request):
    preds = _load_latest_predictions()
    return render(request, "usuarios/index.html", preds)

# ----------------------------
# PERFIL DEL USUARIO
# ----------------------------
@login_required
def perfil_view(request):
    # Asegurarse de que el usuario tenga un Perfil (evita RelatedObjectDoesNotExist)
    perfil = _ensure_perfil(request.user)
    return render(request, "usuarios/perfil.html", {"perfil": perfil})


# ----------------------------
# CAMBIAR PLAN
# ----------------------------
@login_required
def cambiar_plan(request):
    # Asegurarse de que el usuario tenga un Perfil en lugar de fallar
    perfil = _ensure_perfil(request.user)
    planes = Plan.objects.all()

    if request.method == "POST":
        nuevo_plan_id = request.POST.get("plan")
        if not nuevo_plan_id:
            messages.error(request, "Selecciona un plan válido.")
            return redirect('cambiar_plan')
        try:
            nuevo_plan = Plan.objects.get(id=int(nuevo_plan_id))
        except (Plan.DoesNotExist, ValueError):
            messages.error(request, "Plan no encontrado.")
            return redirect('cambiar_plan')

        # Actualizar el plan del perfil existente (no crear usuarios)
        perfil.plan = nuevo_plan
        perfil.save()
        messages.success(request, f"Tu plan ha sido actualizado a {nuevo_plan.nombre}.")
        return redirect("perfil")  # Redirige al perfil después de cambiar el plan

    return render(request, "usuarios/cambiar_plan.html", {"perfil": perfil, "planes": planes})


# ----------------------------
# CAMBIAR CORREO
# ----------------------------
@login_required
def cambiar_correo(request):
    user = request.user
    if request.method == 'POST':
        nuevo_correo = request.POST.get('nuevo_correo')
        if nuevo_correo:
            user.email = nuevo_correo
            user.save()
            messages.success(request, 'Tu correo ha sido actualizado correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor ingresa un correo válido.')
    # Si el usuario no tiene perfil, lo creamos para mantener consistencia en la app
    _ensure_perfil(user)
    return render(request, 'usuarios/cambiar_correo.html')