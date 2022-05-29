# This is an API made using FastAPI.

## To run this app locally on your system, first install fastapi and unicorn

#### Run:  ```pip install fastapi uvicorn```

### Then run the fastapi server using ```uvicorn main:app --reload``` and open the URL on the terminal.

## Endpoints
 - Since this app is made using FastAPI you can visit the route '/docs' to get a list of all endpoints at a single place and test the same.
 - You can test the all below endpoint on the docs page
 - The endpoint '/' returns the Group which is present.
 - The endpoint '/add-expense' accepts a POST Request containing the expense item as JSON. Format for the expense item should be of class **ExpenseItem**.

        class  ExpenseItem(BaseModel):
	        name: str 
		    value: int
		    paid_by: Optional[dict] = {}
		    owed_by: Optional[dict] = {}
 - The endpoint '/create-group' accepts a POST Request containing the group name and optional initial members.
 - The endpoint '/update-expense' accepts a POST Request containing a mandatory expense name and the fields which should be updated.
 - The endpoint '/delete-expense/{expense_name}' accepts a DELETE Request where expense_name is dynamic parameter which can be any of the expense that has been added before.
 - The endpoint '/summary' accepts a GET Request and return a simplified summary of Expensed of every member as JSON Response.