import requests
import json
from fastapi import HTTPException, status
from typing import Optional

def get_kiot_token():
    # URL token
    url = "https://id.kiotviet.vn/connect/token"

    # Thông tin client
    client_id = "54ac15ca-c065-4072-821b-05b162bc6d58"
    client_secret = "EECE108EE229B5CEBFDF58B14C7F501493E5CA43"

    # Header
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Body (dữ liệu gửi kèm request)
    data = {
        "scopes": "PublicApi.Access",
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    # Gửi request POST
    response = requests.post(url, headers=headers, data=data)

    # Xử lý response
    if response.status_code == 200:
        token_info = response.json()
        return token_info.get("access_token")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting KiotViet token: {response.status_code} {response.text}"
        )

def add_customer_to_kiot(user_code, name, phone_number, address, branch_id, access_token):
    url = "https://public.kiotapi.com/customers"

    # Thông tin khách hàng cần tạo
    payload = {
        "code": user_code,
        "name": name,
        "contactNumber": phone_number,
        "address": address,
        "branchId": branch_id
    }

    headers = {
        "Authorization": f"Bearer {access_token}",  # thay bằng token thật
        "Retailer": "sonfaber",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code in [200, 201]:
            customer_data = response.json()
            return {
                "success": True,
                "data": customer_data,
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "error": f"KiotViet API error: {response.status_code} {response.text}",
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}",
            "status_code": None
        }
    
# def get_branch_id_by_name(access_token: str, branch_name: str) -> Optional[int]:
#     """
#     Lấy branch_id từ KiotViet API theo tên chi nhánh
    
#     Args:
#         access_token (str): Access token từ KiotViet
#         branch_name (str): Tên chi nhánh cần tìm
        
#     Returns:
#         Optional[int]: branch_id nếu tìm thấy, None nếu không tìm thấy
        
#     Raises:
#         HTTPException: Khi có lỗi gọi API
#     """
#     url = "https://public.kiotapi.com/branches"
    
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Retailer": "sonfaber",
#         "Content-Type": "application/json"
#     }
    
#     try:
#         response = requests.get(url, headers=headers)
        
#         if response.status_code == 200:
#             data = response.json()
#             branches = data.get("data", [])
            
#             # Tìm chi nhánh theo tên (case-insensitive)
#             for branch in branches:
#                 if branch.get("branchName", "").lower() == branch_name.lower():
#                     return branch.get("id")
            
#             # Không tìm thấy chi nhánh
#             return None
            
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Error getting KiotViet branches: {response.status_code} {response.text}"
#             )
            
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Request failed when getting branches: {str(e)}"
#         )
    


def get_branch_id(access_token: str) -> int:
    """
    Lấy branch_id đầu tiên từ KiotViet API
    
    Args:
        access_token (str): Access token từ KiotViet
        
    Returns:
        int: branch_id
        
    Raises:
        HTTPException: Khi có lỗi gọi API hoặc không có branch nào
    """
    url = "https://public.kiotapi.com/branches"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Retailer": "sonfaber",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            branches = data.get("data", [])
            
            if not branches:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không tìm thấy chi nhánh nào trong KiotViet"
                )
            
            return branches[0]["id"]
            
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting KiotViet branches: {response.status_code} {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Request failed when getting branches: {str(e)}"
        )

def create_kiot_order(access_token, retailer, order_data):
    """
    Tạo đơn đặt hàng đơn giản
    
    Args:
        access_token (str): KiotViet API access token
        retailer (str): KiotViet retailer 
        order_data (dict): Dữ liệu đơn hàng
        
    Returns:
        dict: Kết quả API response
    """
    url = "https://public.kiotapi.com/orders"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Retailer": retailer,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        
        print("✅ Tạo đơn hàng thành công!")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi khi tạo đơn hàng: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Chi tiết lỗi: {e.response.text}")
        return None

def create_order_data(customer_info, products, branch_id=333995):
    """
    Tạo dữ liệu đơn hàng đơn giản
    
    Args:
        customer_info (dict): Thông tin khách hàng
        products (list): Danh sách sản phẩm
        branch_id (int): ID chi nhánh
        
    Returns:
        dict: Dữ liệu đơn hàng
    """

    order_data = {
        "isApplyVoucher":False,
        "branchId": branch_id,
        "discount": 0,
        "method": "Transfer",
        "orderDetails": products,
        "customer": customer_info
    }
    
    return order_data

def get_code_by_name(name, ACCESS_TOKEN, RETAILER):
    """
    Tìm code và retailerId theo tên sản phẩm từ API Kiot.
    Trả về tuple (code, retailerId) nếu tìm thấy, ngược lại trả về None.
    """
    url = "https://public.kiotapi.com/products"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Retailer": RETAILER,
        "Content-Type": "application/json"
    }
    
    try:
        # Gọi API
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Tìm kiếm sản phẩm theo tên
        for item in data.get("data", []):
            if item.get("name", "").lower() == name.lower():
                code = item.get("code")
                retailer_id = item.get("retailerId")
                return (code, retailer_id)
                
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Lỗi decode JSON: {e}")
        return None
    except Exception as e:
        print(f"Lỗi không xác định: {e}")

def create_simple_order(access_token, order_data):
    """
    Tạo đơn đặt hàng đơn giản
    
    Args:
        access_token (str): KiotViet API access token
        retailer_id (str): KiotViet retailer ID
        order_data (dict): Dữ liệu đơn hàng
        
    Returns:
        dict: Kết quả API response
    """
    url = "https://public.kiotapi.com/orders"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Retailer": "sonfaber",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        
        print("✅ Tạo đơn hàng thành công!")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi khi tạo đơn hàng: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Chi tiết lỗi: {e.response.text}")
        return None