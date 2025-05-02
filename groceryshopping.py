import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading
import time
import random
import os

class GroceryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HappyCart Grocery App")
        self.geometry("800x600")
        self.configure(bg="#f8f8f8")
        self.cart = {}
        self.frames = {}

        for Page in (ProductPage, CartPage, SuccessPage):
            frame = Page(parent=self, controller=self)
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(ProductPage)

    def show_frame(self, page):
        self.frames[page].tkraise()
        if page == ProductPage:
            self.frames[ProductPage].refresh_badges()
        elif page == CartPage:
            self.frames[CartPage].update_cart_display()

    def add_to_cart(self, item, price):
        if item in self.cart:
            self.cart[item]['quantity'] += 1
        else:
            self.cart[item] = {'price': price, 'quantity': 1}
        self.frames[ProductPage].refresh_badges()

    def remove_from_cart(self, item):
        if item in self.cart:
            if self.cart[item]['quantity'] > 1:
                self.cart[item]['quantity'] -= 1
            else:
                del self.cart[item]
        self.frames[ProductPage].refresh_badges()


class ProductPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8f8f8")
        self.controller = controller

        tk.Label(self, text="🛒 Welcome to HappyCart", font=("Poppins", 22, "bold"), bg="#f8f8f8", fg="#333").pack(pady=15)

        self.products = {
            "Rice": {"price": 2.0, "image": "C:/Users/admin/Downloads/rice.png"},
            "Milk": {"price": 1.5, "image": "C:/Users/admin/Downloads/milk.png"},
            "Eggs": {"price": 3.0, "image": "C:/Users/admin/Downloads/eggs.png"},
            "Bread": {"price": 2.5, "image": "C:/Users/admin/Downloads/bread.png"},
            "Apples": {"price": 2.2, "image": "C:/Users/admin/Downloads/apple.png"},
            "Carrots": {"price": 1.0, "image": "C:/Users/admin/Downloads/carrots.png"},
            "Tomatoes": {"price": 1.8, "image": "C:/Users/admin/Downloads/tomato.png"},
            "Bananas": {"price": 1.2, "image": "C:/Users/admin/Downloads/banana.png"},
        }

        self.product_images = {}
        self.badges = {}

        canvas = tk.Canvas(self, bg="#f8f8f8", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f8f8f8")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for name, info in self.products.items():
            outer = tk.Frame(self.scrollable_frame, bg="white", padx=10, pady=10, bd=1, relief="solid")
            outer.pack(pady=10, padx=20, fill="x")

            # Load and display image with error handling
            try:
                img_path = info['image']
                if os.path.exists(img_path):
                    img = Image.open(img_path).resize((80, 80))
                    photo = ImageTk.PhotoImage(img)
                    self.product_images[name] = photo  # Store reference to prevent garbage collection
                    tk.Label(outer, image=photo, bg="white").pack(side="left", padx=10)
                else:
                    print(f"Image for {name} not found: {img_path}")
            except Exception as e:
                print(f"Error loading image for {name}: {e}")

            details_frame = tk.Frame(outer, bg="white")
            details_frame.pack(anchor="w", padx=10)

            tk.Label(details_frame, text=name, font=("Poppins", 14, "bold"), bg="white").pack(anchor="w")
            tk.Label(details_frame, text=f"Price: ${info['price']:.2f}", font=("Poppins", 12), bg="white").pack(anchor="w")

            tk.Button(details_frame, text="Add to Cart", bg="#ffcc00", fg="#000", font=("Poppins", 10),
                      relief="raised", bd=2, padx=10, pady=2,
                      command=lambda n=name, p=info["price"]: controller.add_to_cart(n, p)).pack(anchor="w", pady=5)

            badge = tk.Label(details_frame, text="✔️ Added", fg="green", font=("Poppins", 10), bg="white")
            badge.pack(anchor="w")
            badge.pack_forget()
            self.badges[name] = badge

        cart_img = Image.open("C:/Users/admin/Downloads/cart.png").resize((25, 25))
        self.cart_icon = ImageTk.PhotoImage(cart_img)

        tk.Button(self, image=self.cart_icon, text=" Go to Cart", compound="left", font=("Poppins", 14, "bold"),
                  bg="#ff5722", fg="white", padx=10, pady=5, command=lambda: controller.show_frame(CartPage)).pack(pady=20)

    def refresh_badges(self):
        for name in self.products:
            if name in self.controller.cart:
                self.badges[name].pack(anchor="w")
            else:
                self.badges[name].pack_forget()


class CartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        cart_img = Image.open("C:/Users/admin/Downloads/cart.png").resize((30, 30))
        self.cart_icon = ImageTk.PhotoImage(cart_img)

        tk.Label(self, image=self.cart_icon, text=" My Cart", compound="left", font=("Poppins", 22, "bold"),
                 bg="#ffffff").pack(pady=10)

        self.cart_items_frame = tk.Frame(self, bg="#ffffff")
        self.cart_items_frame.pack(pady=10)

        self.total_label = tk.Label(self, text="", font=("Poppins", 16, "bold"), bg="#ffffff")
        self.total_label.pack(pady=5)

        tk.Button(self, text="Proceed to Payment", bg="green", fg="white", font=("Poppins", 12),
                  command=self.proceed_to_payment).pack(pady=10)

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, state="readonly",
                                     values=list(controller.frames[ProductPage].products.keys()))
        self.dropdown.pack(pady=5)
        tk.Button(self, text="Add More Item", command=self.add_more_item).pack()

        tk.Button(self, text="← Back to Shop", font=("Poppins", 10), command=lambda: controller.show_frame(ProductPage)).pack(pady=5)

        tk.Label(self, text="Your needs, Our promise", font=("Poppins", 10), fg="#999", bg="#ffffff").pack(side="bottom", pady=10)

    def update_cart_display(self):
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()

        total = 0
        for item, details in self.controller.cart.items():
            item_total = details['price'] * details['quantity']
            total += item_total

            frame = tk.Frame(self.cart_items_frame, bg="#ffffff")
            frame.pack(fill="x", pady=2, padx=20)

            tk.Label(frame, text=f"{item} x {details['quantity']} = ${item_total:.2f}",
                     font=("Poppins", 12), bg="#ffffff", anchor="w", width=30).pack(side="left")

            tk.Button(frame, text="-", font=("Poppins", 10), width=3,
                      command=lambda i=item: self.modify_item(i, -1)).pack(side="left")
            tk.Button(frame, text="+", font=("Poppins", 10), width=3,
                      command=lambda i=item: self.modify_item(i, 1)).pack(side="left")

        self.total_label.config(text=f"Total: ${total:.2f}")

    def modify_item(self, item, change):
        if change == -1:
            self.controller.remove_from_cart(item)
        elif change == 1:
            self.controller.cart[item]['quantity'] += 1
        self.update_cart_display()

    def add_more_item(self):
        item = self.dropdown_var.get()
        if item:
            price = self.controller.frames[ProductPage].products[item]["price"]
            self.controller.add_to_cart(item, price)
            self.update_cart_display()

    def proceed_to_payment(self):
        if not self.controller.cart:
            messagebox.showwarning("Cart Empty", "Add items to the cart before proceeding.")
            return
        self.controller.cart.clear()
        self.controller.show_frame(SuccessPage)
        self.controller.frames[SuccessPage].start_confetti()


class SuccessPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f5dc")
        self.controller = controller
        self.canvas = tk.Canvas(self, width=800, height=600, bg="#f5f5dc", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.msg1 = tk.Label(self.canvas, text="✅ Payment Successful!", font=("Poppins", 20, "bold"), fg="green", bg="#f5f5dc")
        self.msg1.place(relx=0.5, rely=0.15, anchor="center")

        self.msg2 = tk.Label(self.canvas, text="🚚 Your order is on the way", font=("Poppins", 16), bg="#f5f5dc")
        self.msg2.place(relx=0.5, rely=0.30, anchor="center")

        self.msg3 = tk.Label(self.canvas, text="Thank you for shopping with us!", font=("Cooper", 16), bg="#f5f5dc")
        self.msg3.place(relx=0.5, rely=0.45, anchor="center")

        self.msg4 = tk.Label(self.canvas, text="Don't stay away too long, we miss you already 😊", font=("Poppins", 10), bg="#f5f5dc", fg="#555")
        self.msg4.place(relx=0.5, rely=0.52, anchor="center")

        self.btn_shop = tk.Button(self.canvas, text="Back to Shop", font=("Poppins", 12),
                                  command=lambda: controller.show_frame(ProductPage))
        self.btn_shop.place(relx=0.4, rely=0.7, anchor="center")

        self.btn_exit = tk.Button(self.canvas, text="Exit", font=("Poppins", 10), command=controller.destroy)
        self.btn_exit.place(relx=0.6, rely=0.7, anchor="center")

    def start_confetti(self):
        def confetti():
            circles = []
            for _ in range(100):
                x = random.randint(0, 800)
                y = random.randint(-50, 0)
                color = random.choice(["red", "blue", "green", "yellow", "purple", "orange"])
                size = random.randint(5, 10)
                circle = self.canvas.create_oval(x, y, x + size, y + size, fill=color, outline=color)
                circles.append(circle)

            for _ in range(40):
                for circle in circles:
                    self.canvas.move(circle, 0, 5)
                self.canvas.update()
                time.sleep(0.1)
            for circle in circles:
                self.canvas.delete(circle)

        threading.Thread(target=confetti).start()


if __name__ == "__main__":
    app = GroceryApp()
    app.mainloop()
