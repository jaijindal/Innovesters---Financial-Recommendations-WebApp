from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404
from django.db.models import Sum
from .serializers import TransactionSerializer
from TransApp.models import Transaction

class TransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Transaction.objects.get(id=id, user=self.request.user)
        except Transaction.DoesNotExist:
            raise Http404

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def calculate_quantities(self, user, stock, exclude_transaction_id=None):
        buy_quantity = Transaction.objects.filter(user=user, transaction_type='BUY', stock=stock).exclude(id=exclude_transaction_id).aggregate(Sum('quantity'))['quantity__sum'] or 0
        sell_quantity = Transaction.objects.filter(user=user, transaction_type='SELL', stock=stock).exclude(id=exclude_transaction_id).aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_quantity = buy_quantity - sell_quantity
        return total_quantity

    def error_response(self, message, status):
        return Response({"error": message}, status=status)

    def post(self, request):
        stock = request.data.get('stock')
        if not stock:
            return self.error_response("No stock name provided", status.HTTP_400_BAD_REQUEST)
    
        total_quantity = self.calculate_quantities(request.user, stock)
    
        requested_quantity = int(request.data.get('quantity', 0))
        transaction_type = request.data.get('transaction_type')
    
        if transaction_type == 'SELL' and total_quantity - requested_quantity < 0:
            return self.error_response("This transaction would result in a total quantity less than 0", status.HTTP_400_BAD_REQUEST)
        
        serializer = TransactionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            transaction = serializer.save()
            transaction.user = request.user
            transaction.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        transaction_id = request.data.get('id')
        if not transaction_id:
            return self.error_response("No id provided", status.HTTP_400_BAD_REQUEST)
        
        transaction = self.get_object(transaction_id)
        total_quantity = self.calculate_quantities(request.user, transaction.stock, exclude_transaction_id=transaction_id)

        if transaction.transaction_type == 'BUY' and total_quantity < 0:
            return self.error_response("Deleting this transaction would result in a total quantity less than 0", status.HTTP_400_BAD_REQUEST)
        
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request):
        transaction_id = request.data.get('id')
        if not transaction_id:
            return self.error_response("No id provided", status.HTTP_400_BAD_REQUEST)
    
        transaction = self.get_object(transaction_id)
        old_stock = transaction.stock
        new_stock = request.data.get('stock', old_stock)
    
        # Condition 1: Quantity of the SELL must not be more than the BUY of the stock.
        if request.data.get('transaction_type') == 'SELL':
            new_quantity = int(request.data.get('quantity', transaction.quantity))
            total_quantity = self.calculate_quantities(request.user, new_stock, exclude_transaction_id=transaction_id)
            if total_quantity - new_quantity < 0:
                return self.error_response("This transaction would result in a total quantity less than 0", status.HTTP_400_BAD_REQUEST)
    
        # Condition 2: When stock name changes, check if it will result in the oldstock quantity of BUY being less than the SELL.
        if old_stock != new_stock:
            total_quantity_old_stock = self.calculate_quantities(request.user, old_stock, exclude_transaction_id=transaction_id)
            if total_quantity_old_stock < 0:
                return self.error_response("Changing the stock name would result in a total quantity less than 0 for the old stock", status.HTTP_400_BAD_REQUEST)
    
        # Condition 3: Quantity of the BUY must not reduce the total quantity < 0
        if request.data.get('transaction_type') == 'BUY':
            new_quantity = int(request.data.get('quantity', transaction.quantity))
            total_quantity = self.calculate_quantities(request.user, new_stock, exclude_transaction_id=transaction_id)
            if total_quantity + new_quantity < 0:
                return self.error_response("This transaction would result in a total quantity less than 0", status.HTTP_400_BAD_REQUEST)
    
        serializer = TransactionSerializer(transaction, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
