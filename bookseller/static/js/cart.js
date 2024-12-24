function toggleDropdown(show) {
    const dropdownMenu = document.getElementById('dropdownMenu');
    dropdownMenu.style.display = show ? 'block' : 'none';
}

const accountIcon = document.getElementById('accountIcon');

accountIcon.addEventListener('mouseenter', () => toggleDropdown(true));
accountIcon.addEventListener('mouseleave', () => toggleDropdown(false));



function addToCart( id, name, price,image) {
    event.preventDefault();
    fetch('/api/add-cart', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'price': price,
            'image':image

        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function(res) {
        console.info(res);
        return res.json();
    })
    .then(function(data) {
        console.info(data);
        let counter=document.getElementsByClassName('cartCounter')
        for( let i=0;i<counter.length;i++)
            counter[i].innerText=data.total_quantity
    })
    .catch(function(err) {
        console.error(err);
    });
}
function pay(){
        fetch('/api/pay', {
            method: 'post'
        })
        .then(res => res.json())
        .then(data => {
            if(data.code == 200)
                location.reload();
        })
        .catch(err => { console.error(err);
        }
        );
}
function pay1(){
    if(confirm('Ban Chac Chan Muon Thanh Toan ?')==true){
        fetch('/api/pay1', {
            method: 'post'
        })
        .then(res => res.json())
        .then(data => {
            if(data.code == 200)
                location.reload();
        })
        .catch(err => { console.error(err);
        }
        );
    }
}
function callPay() {
    // Hiển thị modal
    document.getElementById('paymentModal').style.display = 'flex';
}

function closeModal() {
    // Đóng modal
    document.getElementById('paymentModal').style.display = 'none';
}


function updateCart(id,obj){
    fetch('/api/update-cart',{

        method:'put',
        body:JSON.stringify( {
        'id':id,
        'quantity':parseInt(obj.value)

        }),
        headers:{
        'Content-Type': 'application/json'
        }
        }).then(res => res.json()).then(data =>{
            let counter=document.getElementsByClassName('cartCounter');
            for( let i=0;i<counter.length;i++)
                counter[i].innerText=data.total_quantity;
            let amount=document.getElementById('total-amount')
            amount.innerText =new Intl.NumberFormat().format(data.total_amount)
        })
}
function deleteCart(id){
    if(confirm("ban co cac chan xoa k")==true)
    {
         fetch('/api/delete-cart/'+id,{

        method:'delete',

        headers:{
        'Content-Type': 'application/json'
        }
        }).then(res => res.json()).then(data =>{
            let counter=document.getElementsByClassName('cartCounter');
            for( let i=0;i<counter.length;i++)
                counter[i].innerText=data.total_quantity;
            let amount=document.getElementById('total-amount')
            amount.innerText =new Intl.NumberFormat().format(data.total_amount)
             let e =document.getElementById("product"+id)
             e.style.display= "none"
        }).catch(err => console.error(err))
    }

}
//function addComment(productId)
//{
//
//    let content= document.getElementById('commentId')
//
//    if(content!=null)
//    {
//        fetch('/api/comments', {
//    method: 'post',
//    body: JSON.stringify({
//        'product_id': productId,
//        'content': content.value
//    }),
//    headers: {
//        'Content-Type': 'application/json'
//    }
//    })
//    .then(res =>  res.json())
//    .then(data => {
////       console.info(data)
//        if (data.status == 201) {
//            console.log("Comment added successfully:", data.comment);
//            let c = data.comment;
//            let area = document.getElementById('commentArea');
//            area.innerHTML = `
//            <div class="row">
//                <div class="col-md-1 col-xs-4">
//                    <img src="/static/images/1.jpg" class="img-fluid rounded-circle" alt="demo">
//                </div>
//                <div class="col-md-11 col-xs-8">
//                    <p>${c.content}</p>
//                    <p><em>${c.created_date}</em></p>
//                </div>
//            </div>
//            ` + area.innerHTML;
//        } else if (data.status == 404) {
//            alert(data.err_msg);
//        }
//    })
//    .catch(err => {
//        console.error("Fetch error:", err);
//    });
//
//        }
//}
function addComment(productId){
    let content=document.getElementById('commentId')
    fetch('/api/comments',{
       method:'post',
       body:JSON.stringify({
            'product_id': productId,
             'content': content.value
       }),
       headers:{
            'Content-Type':'application/json'
       }
    }).then(res => res.json()).then(data=>{
            console.info(data)

            if(data.status==200){
                let comments=document.getElementById('comments')
                comments.innerHTML=getHtmlComment(data.data)+comments.innerHTML
                content.value=""
            }
            else{
             alert("loi3"+ data.status)
            }
    }).catch(err => {
        console.error(err)
    })
}
function loadComment(productId,page=1){
    fetch(`/api/products/${productId}/comments?page=${page}`).then(res=>res.json()).then(data=>{
        console.info(data)
        let comments=document.getElementById('comments')
        comments.innerHTML= ""
        for( let i=0;i<data.length;i++)
            comments.innerHTML+=getHtmlComment(data[i])
    })
}
function getHtmlComment(comment){
    let image=comment.user.avatar
        if(image === null || !image.startsWith('https'))
            image='/static/images/1.jpg'
        return`<div class="row">
        <div class="col-md-1 col-xs-4">
            <img src="${image}" class="img-fluid rounded-circle" alt="${comment.user.username}">

        </div>
        <div class="col-md-11 col-xs-8">

            <p>${comment.content}</p>
             <p><em>${moment(comment.created_date).locale('vi').fromNow()}</em></p>

        </div>

    </div>`
    }
