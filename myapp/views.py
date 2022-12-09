from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Addcart,Transaction
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.



def initiate_payment(request):
    user=User.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    cart=Addcart.objects.filter(user=user,payment_status=False)
    for i in cart:
    	i.payment_status=True
    	i.save()
    cart=Addcart.objects.filter(user=user,payment_status=False)
    request.session['cart_count']=len(cart)
    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)

def myorders(request):
	user=User.objects.get(email=request.session['email'])
	cart=Addcart.objects.filter(user=user,payment_status=True)
	return render(request,'myorders.html',{'cart':cart})

def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="user":
			products=Product.objects.all()
			return render(request,'index.html',{'products':products})
		else:
			return render(request,'seller_index.html')
	except:
		products=Product.objects.all()
		return render(request,'index.html',{'products':products})

def seller_index(request):
	return render(request,'seller_index.html')

def category(request):
	return render(request,'category.html')

def checkout(request):
	return render(request,'checkout.html')

def cart(request):
	return render(request,'cart.html')

def confirmation(request):
	return render(request,'confirmation.html')

def blog(request):
	return render(request,'blog.html')

def single_blog(request):
	return render(request,'single_blog.html')

def login(request):
	if request.method=='POST':
		try:
			
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.usertype=="user":
					request.session['email']=user.email
					request.session['fname']=user.fname 
					request.session['profile_pic']=user.profile_pic.url
					wishlist=Wishlist.objects.filter(user=user)
					request.session['wishlist_count']=len(wishlist)
					cart=Addcart.objects.filter(user=user,payment_status=False)
					request.session['cart_count']=len(cart)
					return redirect('index')
				else:
					request.session['email']=user.email
					request.session['fname']=user.fname 
					request.session['profile_pic']=user.profile_pic.url
					return redirect('index')
			else:
				msg="Password Is Incorrect"
				return render(request,'login.html',{'msg':msg})
		except:
			msg="Email Not Exists"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def tracking(request):
	return render(request,'tracking.html')

def elements(request):
	return render(request,'elements.html')

def contact(request):
	return render(request,'contact.html')

def signup(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Alredy Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:	
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						profile_pic=request.FILES['profile_pic'],
						usertype=request.POST['usertype']
					)
				msg="Sign Up Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password Does Not Match"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=='POST':
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['cnew_password']
				user.save()
				return redirect('logout')
			else:
				msg="New password & Confirm New password Does Not Match"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old password Incorrect"
			return render(request,'change_password.html',{'msg':msg})

	else:
		return render(request,'change_password.html')

def seller_change_password(request):
	if request.method=='POST':
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['cnew_password']
				user.save()
				return redirect('logout')
			else:
				msg="New password & Confirm New password Does Not Match"
				return render(request,'seller_change_password.html',{'msg':msg})
		else:
			msg="Old password Incorrect"
			return render(request,'seller_change_password.html',{'msg':msg})

	else:
		return render(request,'seller_change_password.html')

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		msg="Profile Update Successfully"
		request.session['fname']=user.fname 
		request.session['profile_pic']=user.profile_pic.url
		return render(request,'profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'profile.html',{'user':user})

def seller_profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		msg="Profile Update Successfully"
		request.session['fname']=user.fname 
		request.session['profile_pic']=user.profile_pic.url
		return render(request,'seller_profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'seller_profile.html',{'user':user})

def seller_add_product(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
				seller=seller,
				product_company=request.POST['product_company'],
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_size=request.POST['product_size'],
				product_image=request.FILES['product_image'],
			)
		msg='Product Add Successfully'
		return render(request,'seller_add_product.html',{'msg':msg})

	else:
		return render(request,'seller_add_product.html')

def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller_view_product.html',{'products':products})

def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_product_detail.html',{'product':product})

def seller_product_edit(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_company=request.POST['product_company']
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_size=request.POST['product_size']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		return render (request,'seller_product_edit.html',{'product':product})
	else:
		return render (request,'seller_product_edit.html',{'product':product})

def seller_product_delete(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller_view_product')

def product_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	product=Product.objects.get(pk=pk)
	try:
		user=User.objects.get(email=request.session['email'])
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass

	try:
		user=User.objects.get(email=request.session['email'])
		Addcart.objects.get(user=user,product=product,payment_status=False)
		cart_flag=True
	except:
		pass
	return render(request,'product_detail.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlist)
	return render(request,'wishlist.html',{'wishlist':wishlist})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.get(user=user,product=product)
	wishlists.delete()
	return redirect('wishlist')

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Addcart.objects.create(
		user=user,
		product=product,
		product_price=product.product_price,
		total_price=product.product_price,
		product_qty=1
		)
	return redirect('cart')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	cart=Addcart.objects.filter(user=user,payment_status=False)
	for i in cart:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(cart)
	return render(request,'cart.html',{'cart':cart,'net_price':net_price})

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Addcart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request,pk):
	cart=Addcart.objects.get(pk=pk)
	product_qty=int(request.POST['product_qty'])
	cart.product_qty=product_qty
	cart.total_price=cart.product_price*product_qty
	cart.save()
	return redirect('cart')