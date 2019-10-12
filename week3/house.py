class House:
    def __init__(self, owner, address, num_of_bedroom):
        self.owner = owner
        self.address = address
        self.last_sold = None
        self.num_of_bedroom = num_of_bedroom
        self.sale = False

    def advertise(self):
        self.sale = True

    def sell(self,name, price):
        if self.sale is True:
            self.owner = name
            self.sale = False
            self.last_sold = price
        else:
            raise Exception
# Rob built a mansion with 6 bedrooms
mansion = House("Rob", "123 Fake St, Kensington", 6)
assert mansion.owner == "Rob"
assert mansion.address == "123 Fake St, Kensington"
assert mansion.num_of_bedroom == 6
assert mansion.sale == False
assert mansion.last_sold == None

# Viv built a 3 bedroom bungalow
bungalow = House("Viv", "42 Wallaby Way, Sydney", 3)
assert bungalow.last_sold == None
assert bungalow.sale == False
# The bungalow is advertised for sale
bungalow.advertise()
assert bungalow.owner == "Viv"
assert bungalow.sale == True


# Hayden tries to buy the mansion but can't
try:
    mansion.sell("Hayden", 3000000)
except Exception:
    print("Hayden is sad")

# He settles for buying the Bungalow instead
bungalow.sell("Hayden", 1000000)
assert bungalow.owner == "Hayden"
assert bungalow.last_sold == 1000000
assert bungalow.sale == False