from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum, Avg
from django.utils import timezone

from .models.estacoes_moveis import EstacoesMoveisIndicador
from .forms import EstacoesMoveisForm

@login_required
def estacoes_moveis_create(request):
    """
    View para criar um novo registro de Estações Móveis.
    """
    if request.method == 'POST':
        form = EstacoesMoveisForm(request.POST)
        if form.is_valid():
            estacoes_moveis = form.save(commit=False)
            estacoes_moveis.criado_por = request.user
            estacoes_moveis.atualizado_por = request.user
            estacoes_moveis.save()
            messages.success(request, 'Indicador de Estações Móveis criado com sucesso!')
            return redirect('estacoes_moveis_list')
    else:
        form = EstacoesMoveisForm()
    
    return render(request, 'questionarios/estacoes_moveis_form.html', {
        'form': form,
        'title': 'Adicionar Indicador de Estações Móveis'
    })

@login_required
def estacoes_moveis_update(request, pk):
    """
    View para atualizar um registro de Estações Móveis existente.
    """
    estacoes_moveis = get_object_or_404(EstacoesMoveisIndicador, pk=pk)
    
    if request.method == 'POST':
        form = EstacoesMoveisForm(request.POST, instance=estacoes_moveis)
        if form.is_valid():
            estacoes_moveis = form.save(commit=False)
            estacoes_moveis.atualizado_por = request.user
            estacoes_moveis.save()
            messages.success(request, 'Indicador de Estações Móveis atualizado com sucesso!')
            return redirect('estacoes_moveis_list')
    else:
        form = EstacoesMoveisForm(instance=estacoes_moveis)
    
    return render(request, 'questionarios/estacoes_moveis_form.html', {
        'form': form,
        'estacoes_moveis': estacoes_moveis,
        'title': 'Editar Indicador de Estações Móveis'
    })

@login_required
def estacoes_moveis_list(request):
    """
    View para listar todos os registros de Estações Móveis.
    """
    estacoes_moveis_list = EstacoesMoveisIndicador.objects.all().order_by('-ano', '-mes', 'operadora')
    
    return render(request, 'questionarios/estacoes_moveis_list.html', {
        'estacoes_moveis_list': estacoes_moveis_list,
        'title': 'Lista de Indicadores de Estações Móveis'
    })

@login_required
def estacoes_moveis_detail(request, pk):
    """
    View para exibir detalhes de um registro de Estações Móveis.
    """
    estacoes_moveis = get_object_or_404(EstacoesMoveisIndicador, pk=pk)
    
    return render(request, 'questionarios/estacoes_moveis_detail.html', {
        'estacoes_moveis': estacoes_moveis,
        'title': 'Detalhes do Indicador de Estações Móveis'
    })

@login_required
def estacoes_moveis_delete(request, pk):
    """
    View para excluir um registro de Estações Móveis.
    """
    estacoes_moveis = get_object_or_404(EstacoesMoveisIndicador, pk=pk)
    
    if request.method == 'POST':
        estacoes_moveis.delete()
        messages.success(request, 'Indicador de Estações Móveis excluído com sucesso!')
        return redirect('estacoes_moveis_list')
    
    return render(request, 'questionarios/estacoes_moveis_confirm_delete.html', {
        'estacoes_moveis': estacoes_moveis,
        'title': 'Confirmar Exclusão'
    })

@login_required
def data_management_view(request):
    """View principal da gestão de dados - lista todos os indicadores"""
    context = {
        'title': 'Central de Gestão de Dados',
        'current_year': timezone.now().year
    }
    return render(request, 'questionarios/data_management.html', context) 