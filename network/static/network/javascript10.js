
function post_post(){
    var post_data = document.querySelector('#post-textarea').value;
    fetch('/postapi', {
        method: 'POST',
        body: JSON.stringify({
            data: post_data
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result['message']);
        document.querySelector('#post-textarea').value = "";
        document.querySelector('#post-alerts').innerHTML = `
            <div class="alert alert-success">
                ${result['message']}
            </div>
        `;
        showfirst();
        setTimeout(() =>{
            document.querySelector('#post-alerts').innerHTML = "";
        }, 5000)
    });
    return false;
}

function showfirst(){
    fetch('/allpostsapi')
        .then(response => response.json())
        .then(posts => {
            var div = document.querySelector('#all-posts');
            var div2 = document.createElement("div");
            div2.innerHTML = `
                <input type="hidden" value="${posts[0].id}" id="post-id">
                <div style="margin:5px 25px 5px 25px;">
                        <a href="/profile/${posts[0].username}/page=1" id="post-username"><h2>${posts[0].username}</h2></a>
                        <p id="postdata" style="white-space: pre-wrap;">${posts[0].data}</p>
                        <b>${posts[0].timeposted}</b><br>
                </div>
                <i class="fa fa-thumbs-up" id="like-btn" onclick="likepost(this)"></i> <span id="like-count">${posts[0].likes}</span>
                <button onclick="edit(this)" class="btn" style="float:right">
                    <img src="https://img.icons8.com/fluent/48/000000/edit.png" height="30px" width="30px"/>
                </button>
            `
            div2.className = 'post-class';
            div2.style.animationName = 'posting';
            div2.style.animationPlayState = 'running';
            div2.style.animationDuration = '3s';
            div2.style.animationFillMode = 'forwards'
            div.removeChild(div.lastElementChild);
            div.insertBefore(div2, div.firstChild);
        });
}

function followtoggle(requesteduser){
    fetch(`/followtoggle/${requesteduser}`)
        .then(response => response.json())
        .then(message => {
            var fbutton = document.querySelector("#follow-btn");
            var followerscount = document.querySelector("#followers-count");
            var count = parseInt(followerscount.innerHTML);
            if(fbutton.innerHTML === "Follow"){
                fbutton.innerHTML = "Un-Follow";
                fbutton.className = "btn btn-danger";
                followerscount.innerHTML = `${count + 1}`;
            }
            else{
                fbutton.innerHTML = "Follow";
                fbutton.className = "btn btn-primary";
                followerscount.innerHTML = `${count - 1}`;
            }
        });
}

function edit(child){
    var parent = child.parentNode;
    var datachild = parent.querySelector('#postdata');
    console.log(datachild);
    var div = document.createElement('div');
    div.innerHTML = `
        <textarea id="post-textarea" cols="215" rows="10">${datachild.innerHTML}</textarea>
        <button onclick="editvalue(this)" class="btn btn-success" id="save-btn">Save</button>
    `
    datachild.replaceWith(div);
}

function editvalue(child){
    var parent = child.parentNode;
    var parentofparent = parent.parentNode;
    var parentofparentofparent = parentofparent.parentNode;
    var childtextarea = parent.querySelector('#post-textarea');
    var postid = parentofparentofparent.querySelector('#post-id');
    fetch(`/editpost/${parseInt(postid.value)}`, {
        method: 'POST',
        body: JSON.stringify({
            newdata: childtextarea.value
        })
    })
        .then(response => response.json())
        .then(result => {
            console.log(result.message);
    })
    var para = document.createElement('p');
    para.innerHTML = childtextarea.value;
    para.id = "postdata";
    para.style.whiteSpace = "pre-wrap";
    para.style.overflow = 'auto';
    parentofparentofparent.querySelector('#save-btn').remove();
    childtextarea.replaceWith(para);
}

function likepost(child){
    var parent = child.parentNode;
    var childid = parent.querySelector('#post-id').value;
    fetch(`/liketoggle/${parseInt(childid)}`)
        .then(response => response.json())
        .then(result => {
            console.log(result.message);
            var likebtn = parent.querySelector('#like-btn');
            var likecount = parent.querySelector('#like-count');
            if(likebtn.style.color === "red" && likebtn.className === "fa fa-thumbs-down")
            {
                likebtn.style.color = "black";
                likebtn.className = "fa fa-thumbs-up";
                likecount.innerHTML = `${parseInt(likecount.innerHTML) - 1}`;
            }
            else
            {
                likebtn.style.color = "red";
                likebtn.className = "fa fa-thumbs-down";
                likecount.innerHTML = `${parseInt(likecount.innerHTML) + 1}`;
            }
        })
}