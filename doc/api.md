# API Documentation for FLOWER4U
## Constants
All api responses follow this format:
	`{"status": "Status", "message": "further info", "data": {json or other form of data}`
	An error response (other than not returning 200) has a status of "error"

## Endpoints
### Home

    Endpoint: /
    Method: GET
    Description: Returns the home page (index.html) No authentication required.

### API Test

    Endpoint: /api
    Methods: GET, POST
    Description: Returns a test message.

### Get Products

Endpoint: /api/products
Method: GET
Description: Returns a list of products based on specified filters.
#### Parameters:

<details><summary>This endpoint defines the folllowing parameters</summary>
  
* filters (optional): An array of filters to apply.
 
  <details><summary>Each filter is a json object consiting of:</summary>
  
  * field: field to act on. Avaliable fields are:  
    1. name  
    2. price  
  	3. stock  
  * rule: Rule to apply to the field. Each field has different valid rules.  
    1. name: contains  
  	2. price: equals, greater, less  
    3. stock: equals, greater, less, exists  
  * value: The value that the rule is applied with  
  		
   *Examples:*  
  1. `{"field": "price", "rule": "less", "value": "1299"}`  
  This filter searches for all products priced less than $12.99  
  2. `{"field": "name", "rule": "contains", "value": "Supreme"}`  
  This filter searches for all products whose name contains the substring Supreme  
  3. `{"field": "stock, "rule": exists, "value": ""}`  
  This filter searches for all produces whose stock is not 0

  <b>NOTE:</b>
  
  1. Each key and value of a filter object are strings  
  2. For the filter : 'stock exists' the value objection is not used but is still required  
  3. The filters in the array are concatinated with AND. Support for OR is not there as of now

* limit (optional): The maximum number of results to return. This will be an integer
* offset (optional): The page offset to start the query. This will be an integer

  <details><summary><b>NOTE:</b></summary>
      
    The actual offset depents on the entered limit.  
    For example if the limit is 10 Offseet 0 would return 0-9 and offset 2 would return 10-19  
  	This is useful for pagination  
      
  </details>
            	
NOTE: The parameters are to be entered in the request body as a json object  
```
{"filters": [{...}, {...}], "limit": 20, "offset": 2}
```

</details>

</details>

#### Returns: data:
A json array consisting of Product objects
```
 "data": [{{"name": "Rose", "price": 3799, "description": "Bunch o' roses", "stock": 95, "location": "url-to"}, {...}]
 ```
#### Normal Status Codes:
* 200: A response has been returned
* 404: The query has returned no data
* 400: A user error. Could be due to an invalid filter, or other problem with the request body, see message for details
	

### Add Product - 

    Endpoint: /api/products
    Method: POST
    Description: Adds a new product.
        Parameters:
            name: The name of the product. (string)
            price: The price of the product. (integer)
            description: The description of the product. (string)
            stock: The stock of the product. (integer)
            location: The location of the product. (string)
            
            NOTE: The paramaters are to be entered in the request body as a json object
            	{"name": "Rose", "price": 3799, "description": "Bunch o' roses", "stock": 95, "location": "url-to"}
        Returns: data: 
        	Empty JSON
        Normal Status Codes:
        	200: Insertion is successfull
        	400: Request data is missing or malformed, see message
          401: Not Logged in
            	

### Get Product - 

    Endpoint: /api/products/<int:product_id>
    Method: GET
    Description: Returns details of a specific product.
        Parameters:
            product_id: The ID of the product. (integer)
          NOTES:
          	For this endpoint the only parameter is in the url.
          	You are still required to send an empty json object {} in the request body
        Returns: data:
        	Single JSON Product object
        	"data": {"name": "Rose", "price": 3799, "description": "Bunch o' roses", "stock": 95, "location": "url-to"}
        Normal Status Codes:
        	200: A product is returned
        	404: No product maching the entered ID was found

### Modify Product - 

    Endpoint: /api/products/<int:product_id>
    Method: PUT
    Description: Modifies details of a specific product.
        Parameters:
            name (optional): The name of the product. (string)
            price (optional): The price of the product. (inetger)
            description (optional): The description of the product. (string)
            stock (optional): The stock of the product. (integer)
            location (optional): The location of the product. (string)
            
          NOTES:
           The paramaters are to be entered in the request body as a json object
            	{"name": "Rose", "price": 3799, "description": "Bunch o' roses"}
           Unentered Parameters are not modified
       Returns: data:
       		Empty JSON object
       Normal Status Codes:
       		200: Product Successfully Updated
       		404: No product found matching the ID
       		400: Request data is missing or malformed, see message
          401: Not Logged in
            	

### Remove Product -

    Endpoint: /api/products/<int:product_id>
    Method: DELETE
    Description: Removes a specific product.
        Parameters:
            product_id: The ID of the product. (integer)
           NOTES:
          	For this endpoint the only parameter is in the url.
          	You are still required to send an empty json object {} in the request body
         Returns: data:
         	"Empty JSON object"
         Normal Status Codes:
         	200: Object Sucessfully Removed
         	404: No product found matching ID
         	400: Request data is missing or malformed, see message
          401: Not Logged in

### Update Product Stock -

    Endpoint: /api/products/<int:product_id>/update-stock
    Method: POST
    Description: Updates the stock of a specific product.
        Parameters:
            product_id: The ID of the product. (integer)
            quantity: The quantity to add or subtract from the current stock. (integer)
            action: Either "add" or "subtract" to indicate whether to add or subtract from the stock. (string)
          NOTES:
          	product_id is entered into the URL the rest must be defined in a json object in the request body
          	If you try to remove more than the stock it will return an error 400
          Examples:
          	url: /api/products/27/update-stock
          	body: {"action": "add", quantity:"23"}
          	Adds 23 to the current stock of the product 27
         Returns: data:
         	"Empty JSON object"
         Normal Status Codes:
         	200: Object Sucessfully updated
         	404: No product found matching ID
         	400: Request data is missing or malformed, see message
          401: Not Logged in or not admin
            

### Buy Product -

    Endpoint: /api/products/buy/<int:product_id>
    Method: POST
    Description: Buys a product by subtracting the quantity from the stock.
        Parameters:
            product_id: The ID of the product. (integer)
            quantity: The quantity of the product to buy. (int)
          NOTES:
          	product_id is entered into the URL quantity must entered as a element in a json obejct in the request body
          	If you try to buy more than the stock it will return an error 400
          	In the future or if possible at all this should be changed to link with a secure payment provider
          	This endpoint requires https
            product_id is entered into the URL the rest must be defined in a json object in the request body
          Examples:
              url: /api/products/buy/12
              body: {"quantity": 2}
              Buys 2 of product # 12
         Returns: data:
         	"Empty JSON object"
         Normal Status Codes:
         	200: Object Sucessfully bought
         	404: No product found matching ID
         	400: Request data is missing or malformed, see message
          401: Not Logged in

### Login -

    Endpoint: /api/user/login
    Method: POST
    Description: Logs in username and password. If login is successful sets the `key` Cookie which is used for authenication at other endpoints.
        Parameters:
            username: Username to log in with
            password: Password to log in with
        NOTES:
           The paramaters are to be entered in the request body as a json object
            	{"username": "BillyBob47", "password": "p@$Sw0rD"}
        Returns: data:
          "Empty JSON object"
        Normal Status Codes:
          200: Successfull Login
          400: Request data is missing or malformed, see message
          404: Username or Password is incorrect
### Register -
    Endpoint: /api/user/register
    method: POST
    Description: Registers a new user. If registration is successful logs the user in. If login is successful sets the `key` Cookie which is used for authenication at other endpoints.
        Parameters:
            username: Username to register
            password: Password for account
            email: Email address for account
        NOTES:
           The paramaters are to be entered in the request body as a json object
            	{"username": "BillyBob47", "password": p@$Sw0rD", "email": "Bob477@example.com"}
        Returns: data:
              "Empty JSON object"
            Normal Status Codes:
              200: Successfull Register and Login
              400: Request data is missing or malformed or username/email already exists, see message for details
          
Authentication

    The API uses a simple key-based authentication. *Include the key in the key cookie provided via login* for authorized access to protected endpoints.
  

Notes

    Ensure that the Content-Type header is set to application/json for relevant requests.
    HTTPS is required for certain endpoints (e.g., buying a product).
    Handle errors appropriately, and check the status and data in the response for each request.
    Each Error provides useful data in the returned json
