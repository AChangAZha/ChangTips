/*
 * @Author: AChangAZha
 * @Date: 2022-06-30 23:10:21
 * @LastEditTime: 2022-08-28 13:22:03
 * @LastEditors: AChangAZha
 */
function getQuery(q) {
    return (window.location.search.match(new RegExp('[?&]' + q + '=([^&]+)')) || [, null])[1];
}
$(function () {
    var Type = getQuery("type")
    var code = getQuery("code")
    function check() {
        $("#" + Type).val($("#" + Type).val().replace(/\s+/g, ''));
        if ($("#PWD").val() && $("#" + Type).val())
            $("#bindClick").removeClass("weui-btn weui-btn_primary weui-btn_disabled").addClass("weui-btn weui-btn_primary");
        else
            $("#bindClick").removeClass("weui-btn weui-btn_primary").addClass("weui-btn weui-btn_primary weui-btn_disabled");
        $("#errorTips").hide();
        $("#errorTips_2").hide();
    }
    var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
    var wxID = "";
    var QB = 1;
    $.ajax({
        url: "/checkCode",
        type: "post",
        data: {
            "code": code,
            "type": Type,
            "csrfmiddlewaretoken": csrftoken
        },
        success: function (data) {
            var res = JSON.parse(data);
            if (res.error)
                location.href = "/error"
            else if (res.hadBind)
                location.href = "/bind/tips"
            else if (res.wxID) {
                wxID = res.wxID
                if (res.ID) {
                    $("#" + Type).val(res.ID)
                }
                if (Type != "css" || res.QB) {
                    $("#bindCI").hide();
                    QB = 0
                }
                if (res.OK) {
                    $("#" + Type).attr("readonly", true);
                    $("#PWD").attr("readonly", true);
                    $("#PTXT").hide()
                    $("#bindClick").hide()
                    $("#formTil").hide()
                    $("#OneKey").show()
                }
                $("#bind").fadeToggle();
            }
            else
                location.href = "/index"
        }
    });
    $("#" + Type).bind('input output', check);
    $("#" + Type).blur(check);
    $("#PWD").bind('input output', check);
    $("#bindClick").click(function () {
        check();
        if ($("#PWD").val() && $("#" + Type).val()) {
            $("#bind").fadeToggle();
            var json = {
                "wxID": wxID,
                "PWD": $("#PWD").val(),
                "csrfmiddlewaretoken": csrftoken
            };
            json[Type] = $("#" + Type).val();
            if (QB == 1 && Type == "css")
                json.QB = $("#ci").is(":checked");
            $.ajax({
                url: "/bind",
                type: "post",
                data: json,
                success: function (data) {
                    var res = JSON.parse(data);
                    if (res.success)
                        if (res.success == "0")
                            location.href = "/error"
                        else
                            location.href = "/bind/success?type=" + Type
                    else {
                        $("#PWD").val("")
                        check()
                        $("#errorTips").show()
                        $("#bind").fadeToggle()
                    }
                }
            })
        }
    });
    $("#oneKeyBtn").click(function () {
        $("#bind").fadeToggle();
        var json = {
            "wxID": wxID,
            "ONE": Type,
            "csrfmiddlewaretoken": csrftoken
        };
        if (QB == 1 && Type == "css")
            json.QB = $("#ci").is(":checked");
        $.ajax({
            url: "/bind",
            type: "post",
            data: json,
            success: function (data) {
                var res = JSON.parse(data);
                if (res.success)
                    if (res.success == "0")
                        location.href = "/error"
                    else
                        location.href = "/bind/success?type=" + Type
                else {
                    $("#PWD").val("")
                    $("#OneKey").hide()
                    check()
                    $("#errorTips_2").show()
                    $("#" + Type).removeAttr("readonly");
                    $("#PWD").removeAttr("readonly");
                    $("#PTXT").show()
                    $("#bindClick").show()
                    $("#formTil").show()
                    $("#bind").fadeToggle()
                }
            }
        })
    });
})