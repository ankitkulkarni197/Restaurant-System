
from collections import deque
from itertools import count

MAX_QUANTITY = 20      # max quantity in one order

MENU = {1: ("Pav Bhaji", 120), 2: ("Fries", 80), 3: ("Masala Dosa", 100),
        4: ("Shev Puri", 60), 5: ("Misal Pav", 90), 6: ("Cold Coffee", 70),
        7: ("Tea", 20)}

QUEUE_LIMIT = max(MENU)      # max orders waiting in the kitchen

customers = {}               # id -> {"name", "orders", "status"}  (active / bill_on_hold / paid)
orders = {}                  # id -> {"customer_id", "item_name", "quantity", "unit_price", "total"}
kitchen_queue = deque()      # waiting order IDs (first in, first out)
served_list = []             # served order IDs

customer_ids = count(101)    # gives 101, 102, 103 ...
order_ids = count(1)         # gives 1, 2, 3 ...


# Asks for a number again and again until the user types a valid one in range.
def get_int(prompt, minimum, maximum=float("inf")):
    while True:
        try:
            number = int(input(prompt).strip())
        except ValueError:
            print("  Invalid input. Please type a whole number.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"  Number must be at least {minimum}." if number < minimum
              else f"  Number must be at most {maximum}.")


# Asks for a name again and again until the user does not leave it blank.   
def get_name(prompt):
    while not (name := input(prompt).strip()):
        print("  Name cannot be empty.")
    return name


# Asks for a customer ID and checks that this customer exists.
def get_customer(prompt):
    customer_id = get_int(prompt, 1)
    if customer_id not in customers:
        print(f"  Customer ID {customer_id} was not found.")
        return None
    return customer_id


# Prints the food menu with item numbers and prices.
def show_menu():
    print("\n" + "=" * 34 + "\n            FOOD MENU\n" + "=" * 34)
    print("\n".join(f"{no:>2}. {name:<18} Rs. {price:>4}" for no, (name, price) in MENU.items()))
    print("=" * 34)


# Prints the main menu options (1 to 7).
def show_main_menu():
    options = ["New customer", "Place an order", "Cancel an order", "Serve next order (kitchen)",
               "Request bill", "View pending orders and served list", "Exit"]
    print("\n" + "-" * 34 + "\n        MAIN MENU\n" + "-" * 34)
    print("\n".join(f"{i}. {text}" for i, text in enumerate(options, 1)))
    print("-" * 34)


# Deletes a waiting order from the queue, orders and the customer's list.
def remove_order(order_id, customer_id):
    kitchen_queue.remove(order_id)
    del orders[order_id]
    customers[customer_id]["orders"].remove(order_id)


# Prints the customer's bill with the grand total and marks them as paid.
def print_bill(customer_id):
    customer = customers[customer_id]
    items = [orders[i] for i in customer["orders"]]
    grand_total = sum(item["total"] for item in items)

    print("\n" + "=" * 52 + f"\n  BILL - {customer['name']} (ID {customer_id})\n" + "=" * 52)
    if items:
        print(f"{'Item':<18}{'Qty':>5}{'Price':>12}{'Total':>14}\n" + "-" * 52)
        for o in items:
            print(f"{o['item_name']:<18}{o['quantity']:>5}"
                  f"{'Rs. ' + str(o['unit_price']):>12}{'Rs. ' + str(o['total']):>14}")
    else:
        print("  No orders were placed.")
    print("-" * 52 + f"\n{'GRAND TOTAL':<35}{'Rs. ' + str(grand_total):>17}\n" + "=" * 52)

    customer["status"] = "paid"
    print("  Thank you! Status is now: paid")


# Prints a table of orders (used for both pending and served lists).
def print_table(order_ids, empty_message):
    if not order_ids:
        print(f"  {empty_message}")
        return
    print(f"{'Order':<7}{'Customer':<16}{'Item':<18}{'Qty':>4}\n" + "-" * 56)
    for i in order_ids:
        o = orders[i]
        print(f"{i:<7}{customers[o['customer_id']]['name']:<16}{o['item_name']:<18}{o['quantity']:>4}")


# Option 1: Adds a new customer and gives them an ID.
def new_customer():
    name = get_name("Enter customer name: ")
    customer_id = next(customer_ids)
    customers[customer_id] = {"name": name, "orders": [], "status": "active"}
    print("\n" + "*" * 34 + f"\n  Customer created: {name}\n  CUSTOMER ID: {customer_id}\n" + "*" * 34)


# Option 2: Takes an item and quantity and adds the order to the kitchen queue.
def place_order():
    customer_id = get_customer("Enter customer ID: ")
    if customer_id is None:
        return
    customer = customers[customer_id]

    if customer["status"] == "bill_on_hold":
        print("  This customer's bill is on hold. Cannot place new orders.")
        return
    if customer["status"] == "paid":
        print("  This customer has already paid. Cannot place new orders.")
        return
    if len(kitchen_queue) >= QUEUE_LIMIT:
        print("  Kitchen cannot take more orders right now")
        return

    show_menu()
    item_no = get_int("Enter item number: ", min(MENU), max(MENU))
    while item_no not in MENU:             
        print("  That item is not on the menu.")
        item_no = get_int("Enter item number: ", min(MENU), max(MENU))
    quantity = get_int(f"Enter quantity (1 to {MAX_QUANTITY}): ", 1, MAX_QUANTITY)
    item_name, unit_price = MENU[item_no]

    order_id = next(order_ids)
    orders[order_id] = {"customer_id": customer_id, "item_name": item_name, "quantity": quantity,
                        "unit_price": unit_price, "total": unit_price * quantity}
    customer["orders"].append(order_id)
    kitchen_queue.append(order_id)

    print(f"\n  Order placed! ORDER ID: {order_id}\n  {quantity} x {item_name} = Rs. {unit_price * quantity}")


# Option 3: Cancels an order only if it is still waiting in the kitchen.
def cancel_order():
    customer_id = get_customer("Enter customer ID: ")
    if customer_id is None:
        return
    order_id = get_int("Enter order ID: ", 1)

    if order_id not in customers[customer_id]["orders"]:
        print(f"  Order {order_id} does not belong to customer {customer_id}.")
    elif order_id in kitchen_queue:
        remove_order(order_id, customer_id)
        print(f"  Order {order_id} has been cancelled.")
    elif order_id in served_list:
        print(f"  Order {order_id} has already been served and cannot be cancelled. It stays on the bill.")
    else:
        print(f"  Order {order_id} was not found.")


# Option 4: Serves the oldest waiting order (first come, first served).
def serve_next_order():
    if not kitchen_queue:
        print("  No orders are waiting in the kitchen.")
        return
    order_id = kitchen_queue.popleft()
    served_list.append(order_id)
    o = orders[order_id]
    print(f"  Served order {order_id}: {o['quantity']} x {o['item_name']} "
          f"for {customers[o['customer_id']]['name']} (ID {o['customer_id']}).")


# Option 5: Gives the bill, or asks what to do if some orders are still waiting.
def request_bill():
    customer_id = get_customer("Enter customer ID: ")
    if customer_id is None:
        return
    customer = customers[customer_id]

    if customer["status"] == "paid":
        print("  This customer has already paid.")
        return

    waiting = [i for i in customer["orders"] if i in kitchen_queue]
    if not waiting:
        print_bill(customer_id)
        return

    print("\n  These orders are still waiting in the kitchen:")
    for i in waiting:
        print(f"    Order {i}: {orders[i]['quantity']} x {orders[i]['item_name']}")
    print("\n  1. Cancel ALL waiting orders and get the bill now"
          "\n  2. Wait until they are served (bill on hold)\n  3. Go back")
    choice = get_int("Enter choice: ", 1, 3)

    if choice == 1:
        for i in waiting:
            remove_order(i, customer_id)
        print(f"  Cancelled {len(waiting)} waiting order(s).")
        print_bill(customer_id)
    elif choice == 2:
        customer["status"] = "bill_on_hold"
        print("  Bill will be ready once your orders are served")


# Option 6: Shows the pending orders and the served orders.
def view_orders():
    print("\n" + "=" * 56 + "\n  PENDING ORDERS (front of the queue first)\n" + "=" * 56)
    print_table(kitchen_queue, "No pending orders.")
    print("\n" + "=" * 56 + "\n  SERVED ORDERS\n" + "=" * 56)
    print_table(served_list, "No orders served yet.")


# Option 7: Prints the goodbye message.
def exit_program():
    print("\nThank you for using the Restaurant Order Management System. Goodbye!")


# Runs the program: shows the menu again and again and calls the chosen option.
def main():
    actions = {1: new_customer, 2: place_order, 3: cancel_order, 4: serve_next_order,
               5: request_bill, 6: view_orders}    # option number -> function

    print("Welcome to the Restaurant Order Management System")
    show_menu()
    try:
        while True:
            show_main_menu()
            choice = get_int("Enter your choice (1-7): ", 1, 7)
            if choice == 7:
                break
            actions[choice]()
    except (KeyboardInterrupt, EOFError):
        pass
    exit_program()


if __name__ == "__main__":
    main()
