$(function() {
    var table_str = "";
    var table_header = "";
    var table_th = "";
    var h3;
    var dataFor;
    var fileArea = $(".fileArea");
    // 创建img标签
    var upLoadImg = document.createElement('img');
    // url参数
    function urlData() {
        var url = location.search;
        var newURL = url.split('?')
        for (var i = 0; i < newURL.length; i++) {
            var index = newURL[i].indexOf('=');
            if (index != -1) {
                return newURL[i].substr(index + 1);
            }
        }
    }
    // 显示图片
    fileChange();

    function fileChange() {
        $('.fileUpload').change(function() {
            var file = this.files[0];
            var fileType = file.type;
            var fileSize = file.size;
            var filename = file.name;
            var reader = new FileReader();
            reader.readAsDataURL(file);
            if(fileType.indexOf('image')==-1){
                showInfo('上传文件格式有误！');
                return;
            }
            if(fileSize>=10485760){
                showInfo('上传文件太大！');
                return;
            }
            reader.onload = function() {
                var base64 = this.result;
                var imgClassify = urlData();
                upLoadImg.src = base64;
                $('.showPreView').append(upLoadImg);
                $('.upLoadFile').hide();
                var baseStr=base64.split(',');
                var baStr=baseStr.pop();
                 $.ajax({
                    url: '/api/ocr/async_analysis/',
                    type: 'POST',
                    data: {fileData:baStr},
                    success: function(msg) {
                        var file_id = msg.data.fid;
                        $('.upInfo').fadeIn();
                        get_ocr_result(file_id);
                    }
                })
            }

        })
    };

    function showInfo(infoText){
        $('.info').fadeIn().html(infoText);
        setTimeout(function(){
            $('.info').hide().html('');
        }, 1000)
    };
        
   function get_ocr_result(fid) {
        var url = '/api/ocr/async_analysis/result/?fid=' + fid + '&type=info';
        $.get(url, function(data) {
            var stringJson=JSON.stringify(data);
                if (data.status == 'error') {
                    return;
                }
                if (data.status == 'running') {
                    setTimeout(function() {
                        get_ocr_result(fid); 
                    }, 1000);
                    return;
                }
                if (data.status == '500') {
                    $('.upInfo>span').html('无法正常识别！');
                    return;
                }
                
                var table_str = "";
                var table_info="";
                var table_header="";
                var numberlist=0;
                table_header='<h3 style="text-align:center;">'+data.data['extra_info']['医院名称']+'</h3>';
                table_info='<tr><td>姓名：'+data.data['extra_info']['姓名']+'</td><td>'+'性别：'+data.data['extra_info']['性别']+'</td><td>'+'年龄：'+data.data['extra_info']['年龄']+'</td></tr><tr><td>'+'检验日期：'+data.data['extra_info']['检验日期']+'</td><td colspan="2">'+'报告日期：'+data.data['extra_info']['报告日期']+'</td></tr>';
                $.each(data.data["indicators"], function(index, data) {
                    $.each(data, function(index1, data2) {
                        numberlist++;
                        table_str += '<tr><td>' + numberlist + '</td><td>' + index1 + '</td><td>' + data2 + '</td><td></td><td></td></tr>';
                    })
                });
                $('.mainTable').before(table_header);
                $('.tab').append(table_info);
                $('.table1').append(table_str);
                $('.mainTable').fadeIn();
                $('.upInfo>span').html('识别完成,已识别'+numberlist+'条信息。');
        });
    }

})
