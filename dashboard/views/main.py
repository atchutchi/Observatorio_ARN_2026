# dashboard/views/main.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.models import User
from questionarios.models import (
    EstacoesMoveisIndicador,
    TrafegoOriginadoIndicador, 
    TrafegoTerminadoIndicador,
    TrafegoRoamingInternacionalIndicador,
    LBIIndicador,
    TrafegoInternetIndicador,
    InternetFixoIndicador,
    TarifarioVozMTNIndicador,  # Corrigido
    TarifarioVozOrangeIndicador,  # Adicionado
    ReceitasIndicador,
    EmpregoIndicador,
    InvestimentoIndicador
)
class DashboardView(LoginRequiredMixin, TemplateView):
   template_name = 'dashboard/home.html'
   
   INDICATOR_MODELS = [
       EstacoesMoveisIndicador,
       TrafegoOriginadoIndicador,
       TrafegoTerminadoIndicador,
       TrafegoRoamingInternacionalIndicador,
       LBIIndicador,
       TrafegoInternetIndicador,
       InternetFixoIndicador,
       TarifarioVozMTNIndicador,
       TarifarioVozOrangeIndicador,
       ReceitasIndicador,
       EmpregoIndicador,
       InvestimentoIndicador
   ]

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['stats'] = self.get_stats()
       context['recent_activities'] = self.get_recent_activities()
       return context

   def get_stats(self):
       # Se é staff/admin, mostrar stats administrativas, senão stats de operadora
       if self.request.user.is_staff:
           return self.get_admin_stats()
       return self.get_operator_stats()

   def get_operator_stats(self):
       operator = self.request.user
       current_month = timezone.now().month
       current_year = timezone.now().year
       
       # Verificar se usuário tem submissões pendentes
       pending_submissions = 0
       for model in self.INDICATOR_MODELS:
           if hasattr(model, 'operadora'):
               exists = model.objects.filter(
                   mes=current_month,
                   ano=current_year
               ).exists()
               if not exists:
                   pending_submissions += 1

       return {
           'pending_submissions': pending_submissions,
           'last_submission': self.get_last_submission_date(operator),
           'license_status': 'Válida'  # Placeholder - implementar lógica real quando necessário
       }

   def get_admin_stats(self):
       # Usar User padrão do Django
       total_operators = User.objects.filter(is_staff=False, is_active=True).count()
       current_month = timezone.now().month
       current_year = timezone.now().year

       monthly_submissions = sum([
           model.objects.filter(
               mes=current_month,
               ano=current_year
           ).count()
           for model in self.INDICATOR_MODELS
       ])

       # Placeholder para aprovações pendentes
       pending_approvals = 0

       expected_submissions = total_operators * len(self.INDICATOR_MODELS)
       compliance_rate = (monthly_submissions / expected_submissions * 100) if expected_submissions > 0 else 0

       return {
           'total_operators': total_operators,
           'monthly_submissions': monthly_submissions,
           'pending_approvals': pending_approvals,
           'compliance_rate': round(compliance_rate, 1)
       }

   def get_recent_activities(self):
       # Implement based on your activity tracking
       return []

   def get_last_submission_date(self, operator):
       dates = []
       
       for model in self.INDICATOR_MODELS:
           latest = model.objects.filter(
               operadora=operator
           ).order_by('-data_criacao').first()
           
           if latest:
               dates.append(latest.data_criacao)
       
       return max(dates) if dates else None