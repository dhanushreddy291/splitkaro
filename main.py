# Install FastAPI and uvicorn using: pip install fastapi uvicorn
# Run a Local API Server using uvicorn main:app --reload

from fastapi import FastAPI, Query
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# The group is a empty dictionary at start
mainGroup = {}

class ExpenseItem(BaseModel):
    name: str
    value: int
    paid_by: Optional[dict] = {}
    owed_by: Optional[dict] = {}


class updateItem(BaseModel):
    name: str
    value: Optional[int] = None
    paid_by: Optional[dict] = None
    owed_by: Optional[dict] = None

@app.get('/')
def index():
    return mainGroup

@app.post('/create-group')
def create_group(
    # Group name consists of Mandaory name and optional initial members list
    group_name: str,
    members: Optional[list] = Query(
        default=[],
        description=
        "Enter the initial members present in the group. Leave empty if None")
):

    if 'name' in mainGroup.keys():
        # If the Group name is already initialized
        return {"Error": "Group already created before"}

    else:
        # Initializing the Group
        mainGroup["name"] = group_name
        mainGroup["items"] = []
        mainGroup["members"] = members
        return mainGroup


@app.post('/add-expense')
def add_expense(expense: ExpenseItem):

    # If the group is not initialized before
    if 'name' not in mainGroup.keys():
        return {"Error": "Create the Group First"}

    elif expense in mainGroup["items"]:
      return {"Error": "Expense item already exists"}

    else:
        # Adding the expense item to the Group
        mainGroup["items"].append(expense)

        # Looping through the persons in this expense and if they are not added befpre to the members list of group, then adding them.
        Paid_by = expense.paid_by
        for key in Paid_by.keys():
            if key not in mainGroup["members"]:
                mainGroup["members"].append(key)
        Owed_by = expense.owed_by
        for key in Owed_by.keys():
            if key not in mainGroup["members"]:
                mainGroup["members"].append(key)
        return mainGroup


@app.put('/update-expense')
async def update_expense(expense: updateItem):

    # If the group is not initialized before
    if 'name' not in mainGroup.keys():
        return {
            "Error": "Create the Group First and add an Expense to Update it"
        }

    else:
        # Looping through the list of expenses to check for which expense to update and then updating it
        N = len(mainGroup["items"])

        for i in range(N):
            if mainGroup["items"][i].name == expense.name:

                # Update the Expense
                if expense.value != None:
                    mainGroup["items"][i].value = expense.value
                if expense.paid_by != None:
                    mainGroup["items"][i].paid_by = expense.paid_by
                    # Looping through the persons in this expense and if they are not added befpre to the members list of group, then adding them.
                    Paid_by = expense.paid_by
                    for key in Paid_by.keys():
                        if key not in mainGroup["members"]:
                            mainGroup["members"].append(key)

                if expense.owed_by != None:
                    mainGroup["items"][i].owed_by = expense.owed_by
                    Owed_by = expense.owed_by
                    for key in Owed_by.keys():
                        if key not in mainGroup["members"]:
                            mainGroup["members"].append(key)

                return mainGroup

        # If expense name is not found in the Group expenses list
        return {"Error": "Expense is not in Group. Please add it first"}


@app.delete('/delete-expense/{expense_name}')
def delete_expense(expense_name: str):
    # If the group is not initialized before
    if 'name' not in mainGroup.keys():
        return {
            "Error": "Create the Group First and initialize it by adding expenses"
        }
    else:
        # Delete the expense by looping through the items which has the given expense name
        N = len(mainGroup["items"])
        for i in range(N):
            if mainGroup["items"][i].name == expense_name:
                del mainGroup["items"][i]
                return mainGroup
        return mainGroup

@app.get("/summary")
def get_summary():
        # If the group is not initialized before
    if 'name' not in mainGroup.keys():
        return {
            "Error": "Create the Group First, initialize it by adding expenses and then get the summary of expenses"
        }
    else: 

      # Function to reduces the chained payments
      # person1 --pays to--> person2 --pays to -->person3
      # would be reduced to person1--pays to -->person3
      # a and b params are the objects of owes and owed by notation
      # Example notation{'A': {'B': 0, 'C': 0}, 'B': {'A': 40, 'C': 0}, 'C': {'A': 20, 'B': 40}}
      def reduce_owes_and_paid_by(a, b, members):
          need_to_pay = a.copy()
          pending_from = b.copy()
          need_to_pay_in_arr = {}
          pending_from_in_arr = {}

          for key in need_to_pay.keys():
              temp = need_to_pay[key]
              arr = []
              for key2 in temp.keys():
                  obj = {}
                  obj['value'] = temp[key2]
                  obj['member'] = key2
                  arr.append(obj)

              need_to_pay_in_arr[key] = arr
              temp = pending_from[key]
              arr = []

              for key2 in temp.keys():
                  obj = {}
                  obj['value'] = temp[key2]
                  obj['member'] = key2
                  arr.append(obj)

              pending_from_in_arr[key] = arr

          for item in need_to_pay_in_arr.keys():
              pay_arr = need_to_pay_in_arr[item]
              get_arr = pending_from_in_arr[item]

              # Sorting the array to get the max values, reducing them and then iterating the same untill it cannot be reduced further
              pay_arr.sort(key=lambda x: x['value'], reverse=True)
              get_arr.sort(key=lambda x: x['value'], reverse=True)

              first_pay = pay_arr[0]
              first_get = get_arr[0]

              while first_pay['value'] > 0 and first_get['value'] > 0:
                  pay = first_pay['value']
                  get = first_get['value']

                  if pay >= get:
                      pay = pay - get
                      first_pay['value'] = pay
                      first_get['value'] = 0

                      getee = pending_from_in_arr[first_pay['member']]

                      for g in getee:
                          if g['member'] == item:
                              g['value'] = pay
                          if g['member'] == first_get['member']:
                              g['value'] = g['value'] + get

                      payee = need_to_pay_in_arr[first_get['member']]

                      for p in payee:
                          if p['member'] == item:
                              p['value'] = 0
                          if p['member'] == first_pay['member']:
                              p['value'] = p['value'] + get
                  else:

                      get = get - pay
                      first_pay['value'] = 0
                      first_get['value'] = get

                      getee = pending_from_in_arr[first_pay['member']]

                      for g in getee:
                          if g['member'] == item:
                              g['value'] = 0
                          if g['member'] == first_get['member']:
                              g['value'] = g['value'] + get

                      payee = need_to_pay_in_arr[first_get['member']]

                      for p in payee:
                          if p['member'] == item:
                              p['value'] = get
                          if p['member'] == first_pay['member']:
                              p['value'] = pay + p['value']

                  pay_arr.pop(0)
                  get_arr.pop(0)
                  get_arr.append(first_get)
                  pay_arr.append(first_pay)
                  pay_arr.sort(key=lambda x: x['value'], reverse=True)
                  get_arr.sort(key=lambda x: x['value'], reverse=True)
                  first_pay = pay_arr[0]
                  first_get = get_arr[0]

          new_a = {}
          new_b = {}

          for n in need_to_pay_in_arr.keys():
              temp = {}
              for n_val in need_to_pay_in_arr[n]:
                  temp[n_val['member']] = n_val['value']
              new_a[n] = temp
              temp = {}
              for n_val in pending_from_in_arr[n]:
                  temp[n_val['member']] = n_val['value']
              new_b[n] = temp

          return [new_a, new_b]
      
      # Util method to get the initial notation of owes object of notatio
      #{'A': {'B': 0, 'C': 0}, 'B': {'A': 0, 'C': 0}, 'C': {'A': 0, 'B': 0}}
      def get_initial_owes(members):
          owes = {}
          for i in members:
              inner = {}
              for j in members:
                  if i != j:
                      inner[j] = 0
              owes[i] = inner
          return owes
      
      # Compute the actual owes based on possitive and negative notation of owes
      def handle_owes_for_obj(owes_obj, obj):
          owes = owes_obj.copy()
          possitive = []
          negative = []
          for key in obj.keys():
              val = {}
              val[key] = obj[key]
              val['value'] = obj[key]
              if obj[key] > 0:
                  possitive.append(val)
              elif obj[key] < 0:
                  negative.append(val)

          negative.sort(key=lambda x: x['value'])
          possitive.sort(key=lambda x: x['value'], reverse=True)

          while len(negative) > 0:
              item1 = negative.pop(0)
              item2 = possitive.pop(0)
              if abs(item1['value']) <= item2['value']:
                  key_negative = next(iter(item1))
                  key_positive = next(iter(item2))
                  prev_obj = owes[key_negative]
                  prev_obj[key_positive] = prev_obj[key_positive] + abs(item1['value'])
                  item2['value'] = item2['value'] - abs(item1['value'])
                  if item2['value'] > 0:
                      possitive.append(item2)
                      possitive.sort(key=lambda x: x['value'], reverse=True)
              else:
                  key_negative = next(iter(item1))
                  key_positive = next(iter(item2))
                  prev_obj = owes[key_negative]
                  prev_obj[key_positive] = prev_obj[key_positive] + abs(item2['value'])
                  item1['value'] = item1['value'] + item2['value']
                  if item1['value'] < 0:
                      negative.append(item1)
                      negative.sort(key=lambda x: x['value'])

          return owes

      def perform_operation(mainGroup):

          # Initializing the 'Balance Summary' object 
          balance_summary = {"name": mainGroup["name"]}
          balances = {}
          default_owes = {}

          for member in mainGroup['members']:
              default_owes[member] = 0

          owes = get_initial_owes(mainGroup['members'])
          owed_by_all = get_initial_owes(mainGroup['members'])

          items = mainGroup['items']
          for item in items:
              paid_by = default_owes.copy()
              owed_by = default_owes.copy()
              paid_by_minus_owed_by = default_owes.copy()

              for key in item.paid_by.keys():
                  paid_by[key] = item.paid_by[key]

              for key in item.owed_by.keys():
                  owed_by[key] = item.owed_by[key]

              for key in paid_by_minus_owed_by.keys():
                  paid_by_minus_owed_by[key] = paid_by[key] - owed_by[key]

              owes = handle_owes_for_obj(owes, paid_by_minus_owed_by)

          for key2 in owes.keys():
              obj = owes[key2]
              for innerKey in obj:
                  owed_by_all[innerKey][key2] = owed_by_all[innerKey][key2] + obj[innerKey]

          (owes, owed_by_all) = reduce_owes_and_paid_by(owes, owed_by_all, mainGroup['members'])

          # keep track of the maount person paid and amount they need to pay to compute balance  
          for member in mainGroup['members']:
              items = mainGroup['items']
              paid = 0
              self_cost = 0
              for item in items:
                  if member in item.paid_by.keys():
                      paid +=  item.paid_by[member]
                  if member in item.owed_by.keys():
                      self_cost += item.owed_by[member]

              balances[member] = {'total_balance': paid - self_cost,
                                  'owes_to': owes[member],
                                  'owed_by': owed_by_all[member]}

          # To remove the owes_to and owed_by in individual members where the values are zero, creating a temporary function
          def cleanup(to_clean):
              for member in balances.keys():
                  sub_members = list(balances[member][to_clean].keys())
                  for sub_member in sub_members:
                      if balances[member][to_clean][sub_member] == 0:
                          del balances[member][to_clean][sub_member]

          # Cleaning up the values
          cleanup("owes_to")
          cleanup("owed_by")

          balance_summary["balances"] = balances
          return balance_summary

      return perform_operation(mainGroup)
