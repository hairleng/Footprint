function oneLog(log_id) {
    console.log("ajax:" + log_id)
    $.ajax({
        url: "/socialnetwork/get-one-log/" + log_id,
        dataType: "json",
        success: updateOnePage,
        error: updateError,
        async: false,
    });
}

function updateOnePage(response) {
    console.log(response)
        // response = response[filter]
    if (Array.isArray(response)) {
        updateOneLog(response)
        updateComment(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function updateOneLog(response) {

    // window.alert(response[0])
    //Each item is a json item like this:
    // {k:v,k:v,k:v.....k:[{},{},{comment3}]}
    $(response).each(function() {
        let my_id = "id_log_text_" + this.log_id

        var mydate = new Date(this.date)
        var local_date = mydate.toLocaleDateString()
        var local_time = mydate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        var already_followed = this.already_followed
        var correct_path = this.log_pic
        if (document.getElementById(my_id) == null) { //If post item is not in the list.
            // window.alert(this.user_id)
            //查重然后prepend
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

            // window.alert(bookmark_function)
            // window.alert(corresponding_like_condition)
            $("#log-list").prepend(
                "<li value='" + this.log_id + "' id='each_log'>" +
                // "<div class='flex flex-row items-center ml-2 w3-padding-16'>" +
                "<a href='/one_log/" + this.log_id + "'>" +
                '<img class=\"w-full h-75 align-left card__image\" src="' + get_log_cover_link.replace("999", this.log_id) +
                '"alt=\'This log does not have a cover picture\' width ="800" height="800">' +
                // " onclick='filterLog(" + this.log_id + "); switchOne();'>" +
                "</a>" +
                '<a href="' + get_profile_link.replace("999", this.username) + '">' +
                "<div class='container'>" +
                "<div class='align-left'>" + '<img src="' + get_profile_photo_link.replace("999", this.user_id - 1) +
                '"alt="This user does not have a cover picture" width ="80" height="80">' +
                "<span><h5 class='font-weight-bold text-primary' id='id_post_profile_" + this.user_id + "'></a>" +
                this.username + "</h5>" + "</span></div>" +
                // "<h6 id='id_post_profile_" + this.user_id + "'>" +
                // this.username + "</h6>" + "</a>"
                "<div>" + follow_button + "</div>" +
                "</div>" +
                "</div>" +
                "<div class = 'container_tri'>" +

                "</div><br>" +
                "<time class='time'>" + local_date + " " + local_time +
                "</time>" +
                "<div class='card__content'>" +
                "<div class='card__title'>" + this.log_title + "<br>" + "📍" + this.log_location + "</div>" +
                "<p class='card_text' id='id_log_text_" + this.log_id + "'>" + this.log_text + "</p>" +
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
                "<div class='keep-two-comments'> <ul id='comment_list_" + this.log_id + "'></ul>" +
                "</div></div>"
                // "<li><img class='left'' src='/" + log_cover_path + "'></div>" +
                //         "<li class='right'>" +
                //         "<h1>"+ this.log_title + "</h1>" +
                //         "<div class='author'><img src='" + profile_path + "'>" +
                //         "<h2>Igor MARTY</h2>" + "</div>" +
                //         "<div class='separator'></div>" +
                //         "<p id='id_log_text_" + this.log_id + "'>" + this.log_text + "</p>" +
                //         // "<ul>" +
                //         // "<li><i class=\"fa fa-heart fa-2x\"></i></li>" +
                //         // "<li><i class=\"fa fa-star-o fa-2x\"></i></li>" +
                //         // "</ul>" +
                //         "<div class='fab'><i class='fa fa-arrow-down fa-3x'> </i>" +
                //         "</div></li>"
            )
        }
    })
}