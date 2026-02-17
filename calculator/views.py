from django.shortcuts import render
from calculator.models import Stock, PurificationRate
from decimal import Decimal
from datetime import datetime

def index(request):
    result = None
    error = None
    selected_stock = None
    amount = None
    date_str = None

    # 1. Fetch all stocks for the dropdown
    stocks = Stock.objects.all().order_by('symbol')

    # 2. Handle the Calculation (POST request)
    if request.method == 'POST':
        try:
            stock_id = request.POST.get('stock')
            amount_str = request.POST.get('amount')
            date_str = request.POST.get('date')

            if stock_id and amount_str and date_str:
                selected_stock = Stock.objects.get(id=stock_id)
                amount = Decimal(amount_str)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                # 3. Find the correct Meezan Rate
                # logic: Find the latest rate that is ON or BEFORE the dividend date
                rate_obj = PurificationRate.objects.filter(
                    stock=selected_stock,
                    effective_date__lte=date_obj
                ).order_by('-effective_date').first()

                if rate_obj:
                    # The Formula
                    charity_amount = amount * (rate_obj.impurity_percentage / 100)
                    
                    result = {
                        'charity_due': round(charity_amount, 2),
                        'rate_used': rate_obj.impurity_percentage,
                        'effective_date': rate_obj.effective_date
                    }
                else:
                    error = "No purification data found for this stock on this date. Please contact Admin."
            else:
                error = "Please fill all fields."
                
        except Exception as e:
            error = f"Calculation Error: {str(e)}"

    return render(request, 'calculator/index.html', {
        'stocks': stocks,
        'result': result,
        'error': error,
        # Pass back input values so form doesn't clear on submit
        'selected_stock_id': int(request.POST.get('stock')) if request.POST.get('stock') else None,
        'entered_amount': amount,
        'entered_date': date_str,
    })