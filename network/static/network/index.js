const edit_post = document.querySelectorAll('#edit_post')
const save_edit = document.querySelectorAll('#save_edit')
const like_buttons = document.querySelectorAll('#like_button')
const user_id = document.querySelector('#user_id')
let count_likes = document.querySelector('#count_likes')

document.addEventListener('DOMContentLoaded', ()=>{
    editPost();
    likePost();
})

function editPost() {
    // attach event listener to edit_post buttons if exists
    if(edit_post){
        edit_post.forEach(button => {
            let postId = button.getAttribute('data-post-id');

            button.addEventListener('click',()=>{
                // hide post paragraph, show textarea
            if(button.parentElement.children[1].style.display == 'none')
            {
                button.parentElement.children[0].style.display = 'none'
                button.parentElement.children[1].style.display = 'block'
                button.parentElement.children[2].style.display = 'block'
                button.parentElement.children[3].innerHTML = 'Cancel'
            }else{
                button.parentElement.children[0].style.display = 'block'
                button.parentElement.children[1].style.display = 'none'
                button.parentElement.children[2].style.display = 'none'
                button.parentElement.children[3].innerHTML = 'Edit'
            }
            save_edit.forEach(button => {
                button.addEventListener('click', ()=>{
                const postObj = {
                    post: button.parentElement.children[1].value,
                    id: postId,
                  }
                
                console.log(postObj)
                const JSONpostObj = JSON.stringify(postObj);
            
                fetch('/edit', {
                method: 'POST',
                body: JSONpostObj
                })
                .then(resp => resp.json())
                .then(result => {console.log(result);
                });
                button.parentElement.children[0].innerHTML = postObj.post

                button.parentElement.children[2].style.display = 'none'
                button.parentElement.children[3].innerHTML = 'Edit'
                button.parentElement.children[1].style.display = 'none'
                button.parentElement.children[0].style.display = 'block'
                })
                
            });


            })
            
        });
    }
}

// like or not like post
function likePost(){
    if(like_buttons){
        count = parseInt(count_likes.textContent)
        like_buttons.forEach(button => {
            let postId = button.getAttribute('data-post-id');
            button.addEventListener('click',()=>{
    
                const likeObj = {
                    post_id: postId,
                    user_id: user_id.innerHTML
                }
    
                const JSONlikeObj = JSON.stringify(likeObj)
    
                fetch('/like', {
                    method: "POST",
                    body: JSONlikeObj
                })
                .then(resp => resp.json())
                .then(result => {
                    if (result.success) {  
                        console.log(result);

                        button.parentElement.children[0].innerHTML = `Likes: <span id="count_likes">${result.new_likes_count}</span>`
                        button.parentElement.children[1].innerHTML = result.like_btn_value
                    }
                });
                
            })
        });
    }
}