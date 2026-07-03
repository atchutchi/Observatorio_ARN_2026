from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from ..forms import ExcelUploadForm
from ..excel_parser import process_excel_file # Import the processing function

@login_required
@permission_required('questionarios.add_trafegointernetindicador', raise_exception=True) # Example permission
def upload_excel_view(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            user = request.user
            
            # Placeholder: Determine operadora if not provided in form/file
            # operadora_code = request.POST.get('operadora') or 'some_default' 
            operadora_code = None # Let parser try to figure it out (or define default)

            results = process_excel_file(excel_file, user, operadora_code)
            
            if results['errors'] == 0:
                messages.success(request, f"{results['processed']} registros processados com sucesso!")
            else:
                messages.warning(request, f"{results['processed']} registros processados, mas ocorreram {results['errors']} erros.")
                # Optionally display detailed errors stored in results['error_details']
                for error_detail in results['error_details']:
                    messages.error(request, error_detail, extra_tags='small') # Show details as smaller errors
            
            return redirect('questionarios:upload_excel') # Redirect back to upload page
    else:
        form = ExcelUploadForm()
        
    return render(request, 'questionarios/upload_excel.html', {'form': form}) 