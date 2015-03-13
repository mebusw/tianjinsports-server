from django.conf.urls import patterns, url

urlpatterns = patterns('peggy.views',
        ### xxx is a rendered page
        ### do_xxx is a restful API


                       url(r'^jsonp$', 'jsonp'),
                       url(r'^save_qiniu_photo$', 'save_qiniu_photo'),
                       url(r'^load_qiniu_photo$', 'load_qiniu_photo'),
                       url(r'^$', 'index'),
                       url(r'^survey$', 'survey'),
                       url(r'^do_survey$', 'do_survey'),
                       url(r'^products/(?P<survey_result_id>\d+)$', 'products'),
                       url(r'^order/(?P<order_id>\d+)$', 'order'),
                       url(r'^express/(?P<order_id>\d+)$', 'express'),
                       url(r'^mine$', 'mine'),
                       url(r'^mine_edit$', 'mine_edit'),
                       url(r'^do_update_mine$', 'do_update_mine'),
                       url(r'^payment_wap$', 'payment_wap'),
                       url(r'^paid_wap$', 'paid_wap'),
                       url(r'^paid_notify_wap$', 'paid_notify_wap'),
                       url(r'^login_page$', 'login_page'),
                       url(r'^do_login$', 'do_login'),
                       url(r'^do_logout$', 'do_logout'),
                       url(r'^registration_page$', 'registration_page'),
                       url(r'^do_send_captcha$', 'do_send_captcha'),
                       url(r'^do_registration$', 'do_registration'),
                       url(r'^article$', 'all_articles'),
                       url(r'^article/(?P<article_id>\d+)$', 'article'),
                       url(r'^bulletin$', 'all_bulletins'),
                       url(r'^bulletin/(?P<article_id>\d+)$', 'bulletin'),
                       url(r'^do_checkin$', 'do_checkin'),
                       url(r'^do_claim_refund$', 'do_claim_refund'),


        #############
                       url(r'^bo$', 'bo_index'),
                       url(r'^bo_login_page$', 'bo_login_page'),
                       url(r'^do_bo_login$', 'do_bo_login'),
                       url(r'^do_bo_logout$', 'do_bo_logout'),
                       url(r'^bo_order/(?P<order_id>\d+)$', 'bo_order'),
                       url(r'^do_bo_update_order/(?P<order_id>\d+)$', 'do_bo_update_order'),
                       url(r'^bo_refund_claims$', 'bo_refund_claims'),
                       url(r'^do_bo_refund/(?P<claim_id>\d+)$', 'do_bo_refund'),
                       url(r'^bo_article$', 'bo_all_articles'),
                       url(r'^bo_article/(?P<article_id>\d+)$', 'bo_article'),


)
