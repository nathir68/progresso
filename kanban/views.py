import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Board, Column, Task

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('boards_list')
    else:
        form = UserCreationForm()
    return render(request, 'kanban/register.html', {'form': form})

@login_required
def boards_list(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            board = Board.objects.create(user=request.user, title=title)
            # Create default columns
            Column.objects.create(board=board, title='To Do', order=0)
            Column.objects.create(board=board, title='In Progress', order=1)
            Column.objects.create(board=board, title='Done', order=2)
            return redirect('board_detail', board_id=board.id)
            
    boards = Board.objects.filter(user=request.user)
    return render(request, 'kanban/boards_list.html', {'boards': boards})

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)
    columns = board.columns.prefetch_related('tasks').all()
    return render(request, 'kanban/board.html', {'board': board, 'columns': columns})

@login_required
@require_POST
def create_task(request):
    data = json.loads(request.body)
    column_id = data.get('column_id')
    title = data.get('title')
    
    column = get_object_or_404(Column, id=column_id, board__user=request.user)
    task = Task.objects.create(column=column, title=title, order=column.tasks.count())
    
    return JsonResponse({'status': 'success', 'task_id': task.id, 'title': task.title})

@login_required
@require_POST
def create_column(request):
    data = json.loads(request.body)
    board_id = data.get('board_id')
    title = data.get('title')
    
    board = get_object_or_404(Board, id=board_id, user=request.user)
    column = Column.objects.create(board=board, title=title, order=board.columns.count())
    
    return JsonResponse({'status': 'success', 'column_id': column.id, 'title': column.title})

@login_required
@require_POST
def move_task(request):
    data = json.loads(request.body)
    task_id = data.get('task_id')
    new_column_id = data.get('new_column_id')
    new_order = data.get('new_order') # List of task IDs in the new column order
    
    task = get_object_or_404(Task, id=task_id, column__board__user=request.user)
    new_column = get_object_or_404(Column, id=new_column_id, board__user=request.user)
    
    task.column = new_column
    task.save()
    
    # Update orders of all tasks in the target column
    if new_order:
        for index, t_id in enumerate(new_order):
            Task.objects.filter(id=t_id, column=new_column).update(order=index)
            
    return JsonResponse({'status': 'success'})
