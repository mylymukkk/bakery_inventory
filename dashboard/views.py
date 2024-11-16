from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

from .models import Product, Batch, Sale, SaleItem, WritenOff
from .forms import CreateProduct, CreateBatch, UpdateBatch, WriteOffProduct

# Create your views here.

@login_required
def index(request):
    page_number = request.GET.get('page', 1)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort', 'name')
    sort_order = request.GET.get('order', 'asc')
    update = request.GET.get('update', 'false')
    
    if update == 'true':
        Product.update_all_product_quantities()     

    items = Product.objects.all()

    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) |  
            Q(category__icontains=query)
        )
       
    if sort_order == 'desc':
        items = items.order_by(f'-{sort_by}')
    else:
        items = items.order_by(sort_by)

    paginator = Paginator(items, 10)
    page_items = paginator.get_page(page_number)

    context = {
        'items': page_items,
        'query': query,
        'sort_by': sort_by,
        'sort_order': sort_order
    }

    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'dashboard/index_table.html', context)
        
    return render(request, 'dashboard/index.html', context)



@login_required
def products(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")
        
    page_number = request.GET.get('page', 1)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort', 'name')
    sort_order = request.GET.get('order', 'asc')

    items = Product.objects.all()

    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) | 
            Q(category__icontains=query) 
        )
                 
    if sort_order == 'desc':
        items = items.order_by(f'-{sort_by}')
    else:
        items = items.order_by(sort_by)

    if request.method == 'POST':
        form = CreateProduct(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard-products')
    else:
        form = CreateProduct()
        
    paginator = Paginator(items, 10)
    page_items = paginator.get_page(page_number)

    context = {
        'items': page_items,
        'form':form,
        'query': query,
        'sort_by': sort_by,
        'sort_order': sort_order
    }

    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'dashboard/products_table.html', context)

    return render(request, 'dashboard/products.html', context)
    
@login_required
def product_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")
    
    try:
        item = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
        
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard-products')
        
    context = {'item':item} 

    return render(request, 'dashboard/product_delete.html', context)
    
@login_required
def product_update(request,pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")

    try:
        item = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")

    if request.method == 'POST':
        form = CreateProduct(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard-products')
    else:
        form = CreateProduct(instance=item)
            
    context = {'form':form}
        
    return render(request, 'dashboard/product_update.html', context)



@login_required
def stock(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")
    
    page_number = request.GET.get('page', 1)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort', 'record_date')
    sort_order = request.GET.get('order', 'desc')
    today_date = datetime.date.today()
    date_range = today_date - datetime.timedelta(days=5)
    
    items = Batch.objects.filter(
        Q(record_date__gte=date_range) | 
        (Q(record_date__lt=date_range) & Q(expiry_date__gte=today_date) & Q(left__gt=0)))

    if query:
        items = items.filter(                
            Q(product__name__icontains=query) |
            Q(product__code__icontains=query) |
            Q(expiry_date__icontains=query)
        )            

    if sort_order == 'desc':
        items = items.order_by(f'-{sort_by}')
    else:
        items = items.order_by(sort_by)   

    if request.method == 'POST':
        form = CreateBatch(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard-stock')
    else:
        form = CreateBatch()

    paginator = Paginator(items, 10)
    page_items = paginator.get_page(page_number)

    context = {
        'items': page_items,
        'today': today_date, 
        'form': form,
        'query': query,
        'sort_by': sort_by,
        'sort_order': sort_order
        }

    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'dashboard/stock_table.html', context)

    return render(request, 'dashboard/stock.html', context)

@login_required
def batch_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")
    
    try:
        item = Batch.objects.get(id=pk)
    except Batch.DoesNotExist:
        raise Http404("Batch does not exist")
    
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard-stock')
    
    context = {'item':item} 

    return render(request, 'dashboard/batch_delete.html', context)

@login_required
def batch_update(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")
    
    try:
        item = Batch.objects.get(id=pk)
    except Batch.DoesNotExist:
        raise Http404("Batch does not exist")
    
    if request.method == 'POST':
        form = UpdateBatch(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard-stock')
    else:
        form = UpdateBatch(instance=item)
    
    context = {'form':form}

    return render(request, 'dashboard/batch_update.html', context)

@login_required
def batch_write_off(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")

    try:
        item = Batch.objects.get(id=pk)
    except Batch.DoesNotExist:
        raise Http404("Batch does not exist")
            
    if request.method == 'POST':
        form = WriteOffProduct(request.POST, batch=item)
        if form.is_valid():
            written_off = form.save(commit=False)  
            written_off.product = item
            written_off.save() 
            return redirect('dashboard-stock')
    else:
        form = WriteOffProduct(batch=item)
    
    context = {
        'form':form,
        'item': item}

    return render(request, 'dashboard/batch_write-off.html', context)



@csrf_exempt
def receive_sales_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sales_data = data.get("sales")
            for sale_entry in sales_data:
                transaction_id = sale_entry.get("transaction_id")
                total_price = sale_entry.get("total_price")
                timestamp = sale_entry.get("timestamp")
                
                sale = Sale.objects.create(transaction_id=transaction_id, total_price=total_price, timestamp=timestamp)

                items = sale_entry.get("items", [])
               
                for item in items:
                    product_code = item.get("product_code")
                    product_name = item.get("product_name")
                    quantity = item.get("quantity")
                    price = item.get("price")

                    SaleItem.objects.create(
                        sale=sale,
                        product_name=product_name,
                        product_code=product_code,
                        quantity=quantity,
                        price=price
                    )

                    batch = Batch.objects.filter(
                        product__code=product_code,
                        expiry_date__gte=datetime.date.today(),
                        left__gt= 0
                    ).order_by('expiry_date', 'record_date').first()

                    if batch:
                        if batch.left >= quantity:
                            batch.left -= quantity
                            batch.save()
                        else:
                            batch.left = 0
                            batch.save()
                                                              
            return JsonResponse({"status":"success"})
        except json.JSONDecodeError:
            return JsonResponse({"status":"error","message": "Invalid JSON"}, status=400)
    return JsonResponse({"status":"error", "message":"Only POST requests are allowed"}, status=405)
    
@login_required
def sales(request):
    page_number = request.GET.get('page', 1)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort', 'timestamp')
    sort_order = request.GET.get('order', 'desc')
    date_range = datetime.datetime.now() - datetime.timedelta(days=5)

    items = Sale.objects.prefetch_related('items').filter(timestamp__gte=date_range)

    if query:
        items = items.filter(
            Q(timestamp__icontains=query) |
            Q(transaction_id__icontains=query) |
            Q(total_price__icontains=query) |
            Q(items__product_name__icontains=query) |
            Q(items__product_code__icontains=query)
        ).distinct()

    if sort_order == 'desc':
        items = items.order_by(f'-{sort_by}')
    else:
        items = items.order_by(sort_by) 

    paginator = Paginator(items, 8)
    page_items = paginator.get_page(page_number)

    context = {
        'items': page_items,
        'query': query,
        'sort_by': sort_by,
        'sort_order': sort_order
        }
    
    if request.headers.get('Hx-Request') == 'true':
            return render(request, 'dashboard/sales_table.html', context)
    
    return render(request, 'dashboard/sales.html', context)



@login_required
def report(request):
    page_number = request.GET.get('page', 1)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort', 'product_name')
    sort_order = request.GET.get('order', 'asc')

    products = Product.objects.all()

    sales_data = request.session.get('sales_data', [])  
    total_profit = request.session.get('total_profit', 0)
    total_loss = request.session.get('total_loss', 0)
    total_revenue = request.session.get('total_revenue', 0)
    start_date_str, end_date_str = request.session.get('start_date'), request.session.get('end_date')
   
    if request.method == 'POST':
        sales_data = []
        total_profit = 0
        total_loss = 0
        total_revenue = 0

        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
 
        if start_date_str and end_date_str:

            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.datetime.combine(datetime.datetime.strptime(end_date_str, "%Y-%m-%d"), datetime.time.max)

            for product in products:
                sales_items = SaleItem.objects.filter(
                    sale__timestamp__gte=start_date,
                    sale__timestamp__lte=end_date,
                    product_code=product.code
                )

                sales_count = sales_items.aggregate(total_sales=Sum('quantity'))['total_sales'] or 0
                            
                written_off_count = WritenOff.objects.filter(
                    record_date__gte=start_date,
                    record_date__lte=end_date,
                    product__product__name=product.name
                ).aggregate(total_written_off=Sum('quantity'))['total_written_off'] or 0
                
                expired_batches = Batch.objects.filter(
                    product=product,
                    expiry_date__lte=end_date,
                    expiry_date__gte=start_date
                ).aggregate(total_expired=Sum('left'))['total_expired'] or 0

                total_written_off = written_off_count + expired_batches

                loss = total_written_off * product.price
                total_loss += loss

                revenue = sum(item.quantity * item.price for item in sales_items)
                total_revenue += revenue

                profit = revenue-loss
                total_profit += profit         
                
                sales_data.append({
                    'product_name': product.name,
                    'product_code': product.code,
                    'sales': sales_count,
                    'written_off': total_written_off,
                    'revenue': float(revenue),
                    'loss': float(loss),
                    'profit': float(profit),
                })

        request.session['sales_data'] = sales_data
        request.session['total_profit'] = float(total_profit)
        request.session['total_loss'] = float(total_loss)
        request.session['total_revenue'] = float(total_revenue)
        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str


    if query:
        sales_data = [
            item for item in sales_data 
            if query.lower() in item['product_name'].lower() or query.lower() in item['product_code']]
        
    if sort_by and sort_order:
        reverse = sort_order == 'desc'
        sales_data = sorted(sales_data, key=lambda x: (x.get(sort_by) is None, x.get(sort_by)), reverse=reverse)

    paginator = Paginator(sales_data, 10)
    page_items = paginator.get_page(page_number)

    context = {
        'items': page_items,
        'total_profit': total_profit,
        'total_loss': total_loss,
        'total_revenue': total_revenue,
        'query': query,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'start_date': start_date_str,
        'end_date': end_date_str
    }

    if request.headers.get('Hx-Request') == 'true':
       return render(request, 'dashboard/report_table.html', context)
       
    return render(request, 'dashboard/report.html', context)


