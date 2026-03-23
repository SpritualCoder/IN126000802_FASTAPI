from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()


# Q1: Root

@app.get("/")
def home():
    return {"message": "Welcome to Speedo Car Rentals"}



# Data

cars = [
    {"id": 1, "model": "Swift", "brand": "Maruti", "type": "Hatchback", "price_per_day": 1500, "fuel_type": "Petrol", "is_available": True},
    {"id": 2, "model": "i20", "brand": "Hyundai", "type": "Hatchback", "price_per_day": 1800, "fuel_type": "Petrol", "is_available": True},
    {"id": 3, "model": "City", "brand": "Honda", "type": "Sedan", "price_per_day": 2500, "fuel_type": "Petrol", "is_available": False},
    {"id": 4, "model": "Verna", "brand": "Hyundai", "type": "Sedan", "price_per_day": 2700, "fuel_type": "Diesel", "is_available": True},
    {"id": 5, "model": "XUV700", "brand": "Mahindra", "type": "SUV", "price_per_day": 3500, "fuel_type": "Diesel", "is_available": True},
    {"id": 6, "model": "Fortuner", "brand": "Toyota", "type": "Luxury", "price_per_day": 5000, "fuel_type": "Diesel", "is_available": False},
]

rentals = []
rental_counter = 1



# Q2: GET /cars

@app.get("/cars")
def get_cars():
    return {
        "total": len(cars),
        "available_count": len([c for c in cars if c["is_available"]]),
        "cars": cars
    }



# Q5: Summary (above dynamic route)

@app.get("/cars/summary")
def summary():
    type_count = {}
    fuel_count = {}

    for c in cars:
        type_count[c["type"]] = type_count.get(c["type"], 0) + 1
        fuel_count[c["fuel_type"]] = fuel_count.get(c["fuel_type"], 0) + 1

    cheapest = min(cars, key=lambda x: x["price_per_day"])
    expensive = max(cars, key=lambda x: x["price_per_day"])

    return {
        "total": len(cars),
        "available": len([c for c in cars if c["is_available"]]),
        "type_breakdown": type_count,
        "fuel_breakdown": fuel_count,
        "cheapest": cheapest,
        "expensive": expensive
    }

@app.get("/cars/filter")
def filter_cars(
    type: Optional[str] = None,
    brand: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = cars

    if type is not None:
        result = [c for c in result if c["type"].lower() == type.lower()]
    if brand is not None:
        result = [c for c in result if c["brand"].lower() == brand.lower()]
    if fuel_type is not None:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]
    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]
    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    return result

@app.get("/cars/unavailable")
def unavailable_cars():
    return [c for c in cars if not c["is_available"]]


# Q16: Search Cars

@app.get("/cars/search")
def search(keyword: str):
    result = [
        c for c in cars
        if keyword.lower() in c["model"].lower()
        or keyword.lower() in c["brand"].lower()
        or keyword.lower() in c["type"].lower()
    ]
    return {"total_found": len(result), "cars": result}


# Q17: Sort Cars

@app.get("/cars/sort")
def sort_cars(sort_by: str = "price_per_day"):
    if sort_by not in ["price_per_day", "brand", "type"]:
        raise HTTPException(400, "Invalid sort field")

    return sorted(cars, key=lambda x: x[sort_by])



# Q18: Pagination

@app.get("/cars/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    return cars[start:end]



# Q20: Combined Browse

@app.get("/cars/browse")
def browse(
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None,
    sort_by: Optional[str] = "price_per_day",
    order: Optional[str] = "asc",
    page: int = 1,
    limit: int = 3
):
    result = cars

    if keyword:
        result = [c for c in result if keyword.lower() in c["model"].lower()]

    if type:
        result = [c for c in result if c["type"].lower() == type.lower()]

    if fuel_type:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]

    if max_price:
        result = [c for c in result if c["price_per_day"] <= max_price]

    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    if sort_by:
        result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(result),
        "page": page,
        "results": result[start:end]
    }



# Q3: GET /cars/{id}

@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = next((c for c in cars if c["id"] == car_id), None)
    if not car:
        raise HTTPException(404, "Car not found")
    return car



# Q4: GET /rentals

@app.get("/rentals")
def get_rentals():
    return {"total": len(rentals), "rentals": rentals}



# Q6: Pydantic Model

class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=30)
    license_number: str = Field(..., min_length=8)
    insurance: bool = False
    driver_required: bool = False


class NewCar(BaseModel):
    model: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    type: str
    price_per_day: int = Field(..., gt=0)
    fuel_type: str
    is_available: bool = True



# Q7: Helper Functions

def find_car(car_id: int):
    return next((c for c in cars if c["id"] == car_id), None)


def calculate_rental_cost(price, days, insurance, driver):
    base = price * days

    discount = 0
    if days >= 15:
        discount = 0.25 * base
    elif days >= 7:
        discount = 0.15 * base

    insurance_cost = 500 * days if insurance else 0
    driver_cost = 800 * days if driver else 0

    total = base - discount + insurance_cost + driver_cost

    return base, discount, insurance_cost, driver_cost, total



# Q8 + Q9: POST /rentals

@app.post("/rentals")
def create_rental(req: RentalRequest):
    global rental_counter

    car = find_car(req.car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    if not car["is_available"]:
        raise HTTPException(400, "Car not available")

    base, discount, ins_cost, drv_cost, total = calculate_rental_cost(
        car["price_per_day"], req.days, req.insurance, req.driver_required
    )

    car["is_available"] = False

    rental = {
        "rental_id": rental_counter,
        "customer": req.customer_name,
        "car_id": car["id"],
        "car": f"{car['brand']} {car['model']}",
        "days": req.days,
        "insurance": req.insurance,
        "driver": req.driver_required,
        "base_cost": base,
        "discount": discount,
        "insurance_cost": ins_cost,
        "driver_cost": drv_cost,
        "total_cost": total,
        "status": "active"
    }

    rentals.append(rental)
    rental_counter += 1

    return rental



# # Q10: Filter

# @app.get("/cars/filter")
# def filter_cars(
#     type: Optional[str] = None,
#     brand: Optional[str] = None,
#     fuel_type: Optional[str] = None,
#     max_price: Optional[int] = None,
#     is_available: Optional[bool] = None
# ):
#     result = cars

#     if type is not None:
#         result = [c for c in result if c["type"].lower() == type.lower()]
#     if brand is not None:
#         result = [c for c in result if c["brand"].lower() == brand.lower()]
#     if fuel_type is not None:
#         result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]
#     if max_price is not None:
#         result = [c for c in result if c["price_per_day"] <= max_price]
#     if is_available is not None:
#         result = [c for c in result if c["is_available"] == is_available]

#     return result



# Q11: Add Car

@app.post("/cars", status_code=201)
def add_car(new_car: NewCar):
    for c in cars:
        if c["model"] == new_car.model and c["brand"] == new_car.brand:
            raise HTTPException(400, "Car already exists")

    new_id = max([c["id"] for c in cars]) + 1

    car = new_car.dict()
    car["id"] = new_id

    cars.append(car)
    return car



# Q12: Update Car

@app.put("/cars/{car_id}")
def update_car(car_id: int, price_per_day: Optional[int] = None, is_available: Optional[bool] = None):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    if price_per_day is not None:
        car["price_per_day"] = price_per_day
    if is_available is not None:
        car["is_available"] = is_available

    return car



# Q13: Delete Car

@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    for r in rentals:
        if r["car_id"] == car_id and r["status"] == "active":
            raise HTTPException(400, "Car has active rental")

    cars.remove(car)
    return {"message": "Car deleted"}

# Q15: Extra Routes

@app.get("/rentals/active")
def active_rentals():
    return [r for r in rentals if r["status"] == "active"]


@app.get("/rentals/by-car/{car_id}")
def rental_by_car(car_id: int):
    return [r for r in rentals if r["car_id"] == car_id]


@app.get("/cars/unavailable")
def unavailable_cars():
    return [c for c in cars if not c["is_available"]]



# Q19: Rentals Search/Sort/Page

@app.get("/rentals/search")
def rental_search(name: str):
    return [r for r in rentals if name.lower() in r["customer"].lower()]


@app.get("/rentals/sort")
def rental_sort(sort_by: str = "total_cost"):
    return sorted(rentals, key=lambda x: x[sort_by])


@app.get("/rentals/page")
def rental_page(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    return rentals[start:end]





# Q14: Return Workflow

@app.get("/rentals/{rental_id}")
def get_rental(rental_id: int):
    r = next((r for r in rentals if r["rental_id"] == rental_id), None)
    if not r:
        raise HTTPException(404, "Rental not found")
    return r


@app.post("/return/{rental_id}")
def return_car(rental_id: int):
    r = next((r for r in rentals if r["rental_id"] == rental_id), None)
    if not r:
        raise HTTPException(404, "Rental not found")

    r["status"] = "returned"

    car = find_car(r["car_id"])
    if car:
        car["is_available"] = True

    return r
















