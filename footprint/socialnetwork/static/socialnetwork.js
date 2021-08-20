function getLogs() {
    $.ajax({
        url: "/socialnetwork/get-logs",
        dataType: "json",
        success: updatePage,
        error: updateError,
    });
}

function getBookmarkLogs() {
    $.ajax({
        url: "/socialnetwork/get-bookmark-logs",
        dataType: "json",
        success: updatePage,
        error: updateError,
    });
}

function getFilteredLogs() {
    $.ajax({
        url: "/socialnetwork/filter-date",
        dataType: "json",
        success: updateFilteredPage,
        error: updateError
    });
}


function updatePage(response) {
    console.log(response)
    if (Array.isArray(response)) {
        updateList(response)
        updateComment(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function updateFilteredPage(response) {
    console.log(response)
        // response = response[filter]
    if (Array.isArray(response)) {
        updateList(response)
        updateComment(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function updateError(xhr, status, error) {
    console.log('Status=' + xhr.status + ' (' + error + ')')
    displayError('Status=' + xhr.status + ' (' + error + ')')
}

function displayError(message) {
    $("#error").html(message);
}

function updateComment(response) {
    $(response).each(function() {
        let my_id = "id_log_text_" + this.log_id
        var log_id = this.log_id
        if (document.getElementById(my_id) != null) {
            console.log(comments)
            var comments = this.comments
            $(comments).each(function() {
                let comment_id = "id_comment_text_" + this.comment_id
                var comment_date = new Date(this.date)
                var local_date = comment_date.toLocaleDateString()
                var local_time = comment_date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    //Check if comment is already in the corresponding post's list.
                if (document.getElementById(comment_id) == null) {
                    //Each this is a comment object now.
                    $("#comment_list_" + log_id).prepend(
                        "<li>" +
                        "<div class='card p-3 mt-2'>" +
                        "<div class='d-flex justify-content-between align-items-center'>" +
                        "<div class='user d-flex flex-row align-items-center'>" +
                        '<img src="' + get_profile_photo_link.replace("999", this.user_id - 1) +
                        '"width ="30" height="30">' +
                        "&nbsp;<a href=get_profile/" + this.username + ">" +
                        "<span><small class='font-weight-bold text-primary' id='id_comment_profile_" + this.comment_id + "'>" +
                        this.username + " " + "&nbsp;</small>" + "</a>" +
                        "<small class='font-weight-bold' id='id_comment_text_" + this.comment_id + "'>" + (this.text) + "</small>" +
                        "</span></div>" +
                        "<small id='id_comment_date_time_" + this.comment_id + "'>" + local_date + " " + local_time + "</small>" +
                        "</div></div></li>"
                    )
                }
            })
        }
    })
}

function updateFollow(response) {
    $(response).each(function() {
        let id_follow_button_ = "id_follow_button_" + this.log_id
            //Find all posts existing on the page
        if (document.getElementById(id_follow_button_) != null) {
            var follow_function = "'Follow("
            var followText = ")'>Follow"
            if (this.already_followed == true) {
                follow_function = "'Unfollow("
                followText = ")'>Unfollow"
            }
            if (this.is_self) {
                corresponding_like_condition = ""
                followText = ">"
            }
            document.getElementById(id_follow_button_).innerHTML = "<button type='submit' id='id_follow_button_" + this.log_id + "' onclick=" + follow_function + this.user_id + followText + "</button>"
        }
    })
}

function updateList(response) {
    $(response).each(function() {
        let my_id = "id_log_text_" + this.log_id

        var mydate = new Date(this.date)
        var local_date = mydate.toLocaleDateString()
        var local_time = mydate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        var already_followed = this.already_followed
        var correct_path = this.log_pic
        if (document.getElementById(my_id) == null && this.visibility) { //If post item is not in the list.
            var log_cover_path = this.log_pic.substring(this.log_pic.indexOf("/") + 1)
            if (log_cover_path === null || log_cover_path == "") {
                log_cover_path = "/static/locationimgs/default_location_1.jpeg"
            }
            var profile_path = this.profile_pic.substring(this.profile_pic.indexOf("/") + 1)
            if (profile_path === null || profile_path == "") {
                profile_path = "/static/profileimgs/default_avatar.png"
            }
            var corresponding_like_condition = "'likeLog("
            if (this.already_liked == true) {
                corresponding_like_condition = "'unlikeLog("
            }

            var bookmark_function = "'Bookmark("
            if (this.bookmark_status == true) {
                bookmark_function = "'unBookmark("
            }
            var follow_function = "'Follow("
            var follow_unfollow_button = ")'>Follow"
            if (this.already_followed) {
                follow_function = "'Unfollow("
                follow_unfollow_button = ")'>Unfollow"
            }
            var heart_emoji = ")'> &#x1F90D; "
            if (this.already_liked) {
                heart_emoji = ")'> &#x2764; "
            }
            var bookmark_emoji = ")'> &#9734; "
            if (this.bookmark_status) {
                bookmark_emoji = ")'> &#11088; "
            }

            if (!this.is_self) {
                var follow_button = "<button type='submit' id='id_follow_button_" + this.log_id + "' " +
                    "onclick=" + follow_function + this.user_id + follow_unfollow_button + "</button>"
            } else {
                var follow_button = ""
            }
            //Get rid of socialnetwork before static/.... path.
            $("#log-list").prepend(
                "<li value='" + this.log_id + "' id='each_log'>" +
                // "<div class='flex flex-row items-center ml-2 w3-padding-16'>" +
                "<a href='/one_log/" + this.log_id + "'>" +
                '<img class=\"w-full h-75 align-left card__image\" src="' + get_log_cover_link.replace("999", this.log_id) +
                '"width ="800" height="800">' +
                "</a>" +
                '<a href="' + get_profile_link.replace("999", this.username) + '">' +
                "<div class='container'>" +
                "<div class='align-left'>" + '<img src="' + get_profile_photo_link.replace("999", this.user_id - 1) +
                '"width="80" height="80">' +
                "<span><h5 class='font-weight-bold text-primary' id='id_post_profile_" + this.user_id + "'></a>" +
                this.username + "</h5>" + "</span></div>" +
                "<div>" + follow_button + "</div>" +
                "</div>" +
                "</div>" +
                "<div class = 'container_tri'>" +
                "</div><br>" +
                "<time class='time'>" + local_date + " " + local_time +
                "</time>" +
                "<div class='card__content'>" +
                "<div class='card__title'>" + this.log_title + "<br>" + "📍" + this.log_location + "</div>" +
                "<div class='autoShowHide'>" +
                "<p class='card_text card' id='id_log_text_" + this.log_id + "'>" + this.log_text + "</p>" + "</div>" +
                "</div>" +

                "</li>" +
                "<div className='keep-two-comments'>" +
                "<div className=\"flex flex-row items-center\">" +
                "<button type='submit' class='emoji' id='id_like_button_" + this.log_id + "' onclick=" + corresponding_like_condition + this.log_id + heart_emoji + this.num_likes + "</button>" +
                "<button type='submit' class='emoji' id='id_bookmark_button_" + this.log_id + "' onclick=" + bookmark_function + this.log_id + bookmark_emoji + "</button>" +
                "<button type='submit' class='emoji' id='id_comment_button_" + this.log_id + "' onclick='addComment(" + this.log_id + ")'>" +
                "💬</button>" +
                "</div>" +
                "<div id=\"padding\" style=\"visibility: hidden;\"> Padding </div>" +
                "<div class='w3-row-padding' style='margin:0 -16px'> <label class='w3-opacity'><b></b></label><br>" +
                "<input contenteditable='true' class='w3-border w3-padding items-center' size='100' id='id_comment_input_text_" + this.log_id + "' name='comment'><br><br></div>" +
                "<div class='comment-container'> <ul id='comment_list_" + this.log_id + "'></ul>" +
                "</div></div>"
            )
        }
    })
}

function filterDate(startDate, endDate) {
    console.log(startDate, endDate)
    $.ajax({
        url: "/socialnetwork/filter-date",
        type: "POST",
        data: "start_date=" + startDate + "&end_date=" + endDate + "&csrfmiddlewaretoken=" + getCSRFToken(),
        dataType: "json",
        success: updateFilteredPage,
        error: updateError
    });
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}


function Follow(user_id) {
    if (typeof user_id === 'number') {
        $.ajax({
            url: "/socialnetwork/ajax-follow",
            type: "POST",
            data: "user_id=" + user_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: updateFollow,
            error: updateError
        });
    }
}

function Unfollow(user_id) {
    if (typeof user_id === 'number') {
        $.ajax({
            url: "/socialnetwork/ajax-unfollow",
            type: "POST",
            data: "user_id=" + user_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: updateFollow,
            error: updateError
        });
    }
}

function addComment(log_id) {
    console.log(log_id)
    console.log("Hey")
    if (typeof log_id === 'number') {
        let comment_text = $("#id_comment_input_text_" + log_id)
        let commentTextValue = comment_text.val()
            // Clear input box and old error message (if any)
        comment_text.val('')
        displayError('');

        $.ajax({
            url: "/socialnetwork/add-comment",
            type: "POST",
            data: "comment_text=" + commentTextValue + "&log_id=" + log_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: updateComment,
            error: updateError
        });
    }
}


function Bookmark(log_id) {
    if (typeof log_id === 'number') {
        let html_log_id = $("#id_log" + log_id)
        // Clear input box and old error message (if any)
        displayError('');

        $.ajax({
            url: "/socialnetwork/bookmark",
            type: "POST",
            data: "log_id=" + log_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: updateLikeandBookmarkButton,
            error: updateError
        });
    }
}

function unBookmark(log_id) {
    if (typeof log_id === 'number') {
        let html_log_id = $("#id_log" + log_id)
        // Clear input box and old error message (if any)
        displayError('');

        $.ajax({
            url: "/socialnetwork/unbookmark",
            type: "POST",
            data: "log_id=" + log_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: updateLikeandBookmarkButton,
            error: updateError
        });
    }
}

function likeLog(log_id) {
    if (typeof log_id === 'number') {
        let html_log_id = $("#id_log" + log_id)
        displayError('');
        $.ajax({
            url: "/socialnetwork/like-log",
            type: "POST",
            data: "log_id=" + log_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: updateLikeandBookmarkButton,
            error: updateError
        });
    }
}

function updateLikeandBookmarkButton(response) {
    $(response).each(function() {
        let like_button_id = "id_like_button_" + this.log_id
        if (document.getElementById(like_button_id) != null) {
            var corresponding_like_condition = "'likeLog("
            if (this.already_liked == true) {
                corresponding_like_condition = "'unlikeLog("
            }
            var heart_emoji = ")'> &#x1F90D; "
            if (this.already_liked) {
                heart_emoji = ")'> &#x2764; "
            }
            document.getElementById(like_button_id).innerHTML = "<button type='submit' id='id_like_button_" + this.log_id + "' onclick=" + corresponding_like_condition + this.log_id + heart_emoji + this.num_likes + "</button>"
        }
        let bookmark_button_id = "id_bookmark_button_" + this.log_id
        if (document.getElementById(bookmark_button_id) != null) {
            var bookmark_function = "'Bookmark("
            if (this.bookmark_status == true) {
                bookmark_function = "'unBookmark("
            }
            var bookmark_emoji = ")'> &#9734; "
            if (this.bookmark_status) {
                bookmark_emoji = ")'> &#11088; "
            }
            document.getElementById(bookmark_button_id).innerHTML = "<button type='submit' id='id_bookmark_button_" + this.log_id + "' onclick=" + bookmark_function + this.log_id + bookmark_emoji + "</button>"
        }

    })

}

function unlikeLog(log_id) {
    if (typeof log_id === 'number') {
        let html_log_id = $("#id_log" + log_id)
        displayError('');
        $.ajax({
            url: "/socialnetwork/unlike-log",
            type: "POST",
            data: "log_id=" + log_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: updateLikeandBookmarkButton,
            error: updateError
        });
    }
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}