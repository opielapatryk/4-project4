const post_container = document.querySelector('#post_container')
const edit_post = document.querySelector('#edit_post')
const post = document.querySelector('#post')
const post_textarea = document.querySelector('#post_textarea')
const save_edit = document.querySelector('#save_edit')
const post_id = document.querySelector('#post_id')
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
        edit_post.onclick = () => {
            // hide post paragraph, show textarea
            if(post_textarea.style.display == 'none')
            {
                post.style.display = 'none'
                post_textarea.style.display = 'block'
                save_edit.style.display = 'block'
                edit_post.innerHTML = 'Cancel'
            }else{
                post.style.display = 'block'
                post_textarea.style.display = 'none'
                edit_post.innerHTML = 'Edit'
                save_edit.style.display = 'none'
            }

            save_edit.addEventListener('click', ()=>{
                // post changes
                const postObj = {
                    post: post_textarea.value,
                    id: post_id.innerHTML,
                  }
                
                const JSONpostObj = JSON.stringify(postObj);
            
                fetch('/edit', {
                method: 'POST',
                body: JSONpostObj
                })
                .then(resp => resp.json())
                .then(result => {console.log(result);
                });
                post.textContent = postObj.post

                save_edit.style.display = 'none'
                edit_post.innerHTML = 'Edit'
                post_textarea.style.display = 'none'
                post.style.display = 'block'
                

            })
        }
    }
}

// like or not like post
function likePost(){
    if(like_buttons){
        count_likes = parseInt(count_likes.textContent)
        like_buttons.forEach(element => {
            element.addEventListener('click',()=>{
                
                count_likes += 1
    
                const likeObj = {
                    post_id: post_id.innerHTML,
                    user_id: user_id.innerHTML
                }
    
                const JSONlikeObj = JSON.stringify(likeObj)
    
                fetch('/like', {
                    method: "POST",
                    body: JSONlikeObj
                })
                .then(resp => resp.json())
                .then(result => {console.log(result);
                });
    
                count_likes.textContent = count_likes
                    
                
            })
        });
    }
}