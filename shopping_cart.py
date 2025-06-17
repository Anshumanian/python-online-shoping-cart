import json
from abc import ABC

class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, quantity_available: int):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_available = quantity_available

    @property
    def product_id(self):
        return self._product_id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def quantity_available(self):
        return self._quantity_available

    @quantity_available.setter
    def quantity_available(self, value):
        if value >= 0:
            self._quantity_available = value

    def decrease_quantity(self, amount):
        if amount > 0 and self._quantity_available >= amount:
            self._quantity_available -= amount
            return True
        return False

    def increase_quantity(self, amount):
        if amount > 0:
            self._quantity_available += amount

    def display_details(self):
        return f"[{self.product_id}] {self.name} - ${self.price:.2f} | In Stock: {self.quantity_available}"

    def to_dict(self):
        return {
            "type": "product",
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity_available": self.quantity_available
        }


class PhysicalProduct(Product):
    def __init__(self, product_id, name, price, quantity_available, weight):
        super().__init__(product_id, name, price, quantity_available)
        self._weight = weight

    @property
    def weight(self):
        return self._weight

    def display_details(self):
        return f"[{self.product_id}] {self.name} - ${self.price:.2f}, Weight: {self.weight}kg | Stock: {self.quantity_available}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"type": "physical", "weight": self.weight})
        return data


class DigitalProduct(Product):
    def __init__(self, product_id, name, price, quantity_available, download_link):
        super().__init__(product_id, name, price, quantity_available)
        self._download_link = download_link

    @property
    def download_link(self):
        return self._download_link

    def display_details(self):
        return f"[{self.product_id}] {self.name} - ${self.price:.2f} | Download: {self.download_link}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"type": "digital", "download_link": self.download_link})
        return data


class CartItem:
    def __init__(self, product: Product, quantity: int):
        self._product = product
        self._quantity = quantity

    @property
    def product(self):
        return self._product

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value >= 0:
            self._quantity = value

    def calculate_subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"Item: {self.product.name}, Quantity: {self.quantity}, Price: ${self.product.price}, Subtotal: ${self.calculate_subtotal():.2f}"

    def to_dict(self):
        return {
            "product_id": self.product.product_id,
            "quantity": self.quantity
        }


class ShoppingCart:
    def __init__(self, product_catalog_file='products.json', cart_state_file='cart.json'):
        self._items = {}
        self._product_catalog_file = product_catalog_file
        self._cart_state_file = cart_state_file
        self.catalog = self._load_catalog()
        self._load_cart_state()

    def _load_catalog(self):
        try:
            with open(self._product_catalog_file, 'r') as f:
                data = json.load(f)
                catalog = {}
                for p in data:
                    if p['type'] == 'physical':
                        product = PhysicalProduct(p['product_id'], p['name'], p['price'], p['quantity_available'], p['weight'])
                    elif p['type'] == 'digital':
                        product = DigitalProduct(p['product_id'], p['name'], p['price'], p['quantity_available'], p['download_link'])
                    else:
                        product = Product(p['product_id'], p['name'], p['price'], p['quantity_available'])
                    catalog[p['product_id']] = product
                return catalog
        except FileNotFoundError:
            return {}

    def _load_cart_state(self):
        try:
            with open(self._cart_state_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    product = self.catalog.get(item['product_id'])
                    if product:
                        self._items[item['product_id']] = CartItem(product, item['quantity'])
        except FileNotFoundError:
            pass

    def _save_catalog(self):
        with open(self._product_catalog_file, 'w') as f:
            json.dump([p.to_dict() for p in self.catalog.values()], f, indent=2)

    def _save_cart_state(self):
        with open(self._cart_state_file, 'w') as f:
            json.dump([item.to_dict() for item in self._items.values()], f, indent=2)

    def add_item(self, product_id, quantity):
        product = self.catalog.get(product_id)
        if product and product.quantity_available >= quantity:
            if product_id in self._items:
                self._items[product_id].quantity += quantity
            else:
                self._items[product_id] = CartItem(product, quantity)
            product.decrease_quantity(quantity)
            self._save_cart_state()
            return True
        return False

    def remove_item(self, product_id):
        if product_id in self._items:
            item = self._items.pop(product_id)
            item.product.increase_quantity(item.quantity)
            self._save_cart_state()
            return True
        return False

    def update_quantity(self, product_id, new_quantity):
        if product_id in self._items:
            item = self._items[product_id]
            diff = new_quantity - item.quantity
            if diff > 0 and item.product.quantity_available >= diff:
                item.product.decrease_quantity(diff)
                item.quantity = new_quantity
                self._save_cart_state()
                return True
            elif diff < 0:
                item.product.increase_quantity(-diff)
                item.quantity = new_quantity
                self._save_cart_state()
                return True
        return False

    def get_total(self):
        return sum(item.calculate_subtotal() for item in self._items.values())

    def display_cart(self):
        if not self._items:
            print("Your cart is empty.")
            return
        for item in self._items.values():
            print(item)
        print(f"Total: ${self.get_total():.2f}")

    def display_products(self):
        if not self.catalog:
            print("No products available.")
            return
        for product in self.catalog.values():
            print(product.display_details())


def main():
    cart = ShoppingCart()

    while True:
        print("\n1. View Products")
        print("2. Add Item to Cart")
        print("3. View Cart")
        print("4. Update Quantity")
        print("5. Remove Item")
        print("6. Checkout (dummy)")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            cart.display_products()
        elif choice == '2':
            pid = input("Enter product ID: ")
            qty = int(input("Enter quantity: "))
            if cart.add_item(pid, qty):
                print("Item added.")
            else:
                print("Could not add item. Check availability.")
        elif choice == '3':
            cart.display_cart()
        elif choice == '4':
            pid = input("Enter product ID: ")
            qty = int(input("Enter new quantity: "))
            if cart.update_quantity(pid, qty):
                print("Quantity updated.")
            else:
                print("Failed to update quantity.")
        elif choice == '5':
            pid = input("Enter product ID: ")
            if cart.remove_item(pid):
                print("Item removed.")
            else:
                print("Item not found.")
        elif choice == '6':
            print("Checkout successful! \nTHANK YOU\nHave a nice day")
            break
        elif choice == '7':
            break
        else:
            print("Invalid choice.\nTry again")


if __name__ == '__main__':
    main()
