Search.setIndex({docnames:["chat_client","chat_server","client","client.client","client.client_gui","client.client_gui_processor","client.client_thread","db","db.base","db.client","db.client_history","db.contacts","db.messages","index","log","log.log","log.log_config","messages","run_clients","server","server.server","server.server_gui","server.server_gui_processor","server.server_thread","services","test","test.test_client","test.test_server"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["chat_client.rst","chat_server.rst","client.rst","client.client.rst","client.client_gui.rst","client.client_gui_processor.rst","client.client_thread.rst","db.rst","db.base.rst","db.client.rst","db.client_history.rst","db.contacts.rst","db.messages.rst","index.rst","log.rst","log.log.rst","log.log_config.rst","messages.rst","run_clients.rst","server.rst","server.server.rst","server.server_gui.rst","server.server_gui_processor.rst","server.server_thread.rst","services.rst","test.rst","test.test_client.rst","test.test_server.rst"],objects:{"":{chat_client:[0,0,0,"-"],chat_server:[1,0,0,"-"],client:[2,0,0,"-"],db:[7,0,0,"-"],log:[14,0,0,"-"],messages:[17,0,0,"-"],run_clients:[18,0,0,"-"],server:[19,0,0,"-"],services:[24,0,0,"-"],test:[25,0,0,"-"]},"client.client":{Client:[3,2,1,""]},"client.client.Client":{action_handler:[3,3,1,""],add_contact:[3,3,1,""],authenticate:[3,3,1,""],authenticated:[3,3,1,""],close:[3,3,1,""],del_contact:[3,3,1,""],feed_data:[3,3,1,""],get_contacts:[3,3,1,""],get_data:[3,3,1,""],get_messages:[3,3,1,""],join:[3,3,1,""],leave:[3,3,1,""],on_msg:[3,3,1,""],presence:[3,3,1,""],response_processor:[3,3,1,""],send_key:[3,3,1,""],send_message:[3,3,1,""],sender:[3,3,1,""]},"client.client_gui":{ClientMainWindow:[4,2,1,""]},"client.client_gui.ClientMainWindow":{add_log:[4,3,1,""],add_to_contacts:[4,3,1,""],cancel_profile:[4,3,1,""],change_search:[4,3,1,""],closeEvent:[4,3,1,""],connecting:[4,3,1,""],contact_selected:[4,3,1,""],data_handler:[4,3,1,""],del_contact:[4,3,1,""],feed_data:[4,3,1,""],get_filter_users:[4,3,1,""],is_contact:[4,3,1,""],is_not_contact:[4,3,1,""],load_config:[4,3,1,""],on_auth:[4,3,1,""],on_msg:[4,3,1,""],save_profile:[4,3,1,""],send_message:[4,3,1,""],show_contacts:[4,3,1,""],show_filter_users:[4,3,1,""],toggle_login_widget:[4,3,1,""],toggle_profile:[4,3,1,""],update_chat:[4,3,1,""]},"client.client_gui_processor":{ClientGuiProcessor:[5,2,1,""]},"client.client_gui_processor.ClientGuiProcessor":{action_handler:[5,3,1,""],feed_data:[5,3,1,""],get_history:[5,3,1,""],get_users:[5,3,1,""]},"client.client_thread":{ClientThread:[6,2,1,""]},"client.client_thread.ClientThread":{run:[6,3,1,""]},"db.client":{Client:[9,2,1,""],ClientStorage:[9,2,1,""]},"db.client.Client":{Contacts:[9,4,1,""],Message:[9,4,1,""],id:[9,4,1,""],is_admin:[9,4,1,""],login:[9,4,1,""],password:[9,4,1,""],status:[9,4,1,""]},"db.client.ClientStorage":{add_client:[9,3,1,""],auth_client:[9,3,1,""],filter_clients:[9,3,1,""],get_all:[9,3,1,""],get_client:[9,3,1,""],set_status:[9,3,1,""]},"db.client_history":{ClientHistory:[10,2,1,""],ClientHistoryStorage:[10,2,1,""]},"db.client_history.ClientHistory":{Client:[10,4,1,""],client_id:[10,4,1,""],id:[10,4,1,""],ip_address:[10,4,1,""],when:[10,4,1,""]},"db.client_history.ClientHistoryStorage":{add_record:[10,3,1,""],get_history:[10,3,1,""]},"db.contacts":{ContactStorage:[11,2,1,""],Contacts:[11,2,1,""]},"db.contacts.ContactStorage":{add_contact:[11,3,1,""],del_contact:[11,3,1,""],get_contacts:[11,3,1,""]},"db.contacts.Contacts":{Client:[11,4,1,""],client_id:[11,4,1,""],id:[11,4,1,""],owner_id:[11,4,1,""]},"db.messages":{Message:[12,2,1,""],MessageStorage:[12,2,1,""]},"db.messages.Message":{Client:[12,4,1,""],from_id:[12,4,1,""],id:[12,4,1,""],message:[12,4,1,""],to_id:[12,4,1,""],when:[12,4,1,""]},"db.messages.MessageStorage":{add_message:[12,3,1,""],get_chat_msg:[12,3,1,""],get_from_owner_messages:[12,3,1,""],get_to_owner_msg_from_time:[12,3,1,""],get_to_user_messages:[12,3,1,""]},"log.log":{configure_logging:[15,1,1,""]},"log.log_config":{log_config:[16,1,1,""],log_default:[16,1,1,""],proc:[16,1,1,""]},"messages.AddContact":{action:[17,4,1,""],time:[17,4,1,""],username:[17,4,1,""]},"messages.AdminGetHistory":{action:[17,4,1,""],history:[17,4,1,""],time:[17,4,1,""],user:[17,4,1,""]},"messages.AdminGetUsers":{action:[17,4,1,""],time:[17,4,1,""],users:[17,4,1,""]},"messages.Authenticate":{action:[17,4,1,""],alert:[17,4,1,""],password:[17,4,1,""],result:[17,4,1,""],time:[17,4,1,""],username:[17,4,1,""]},"messages.DelContact":{action:[17,4,1,""],time:[17,4,1,""],username:[17,4,1,""]},"messages.FilterClients":{action:[17,4,1,""],pattern:[17,4,1,""],time:[17,4,1,""],users:[17,4,1,""]},"messages.GetContacts":{action:[17,4,1,""],contacts:[17,4,1,""],login:[17,4,1,""],time:[17,4,1,""]},"messages.GetMessages":{action:[17,4,1,""],from_:[17,4,1,""],time:[17,4,1,""]},"messages.Join":{action:[17,4,1,""],room:[17,4,1,""],time:[17,4,1,""]},"messages.Leave":{action:[17,4,1,""],room:[17,4,1,""],time:[17,4,1,""]},"messages.Msg":{action:[17,4,1,""],from_:[17,4,1,""],text:[17,4,1,""],time:[17,4,1,""],to:[17,4,1,""]},"messages.Presence":{action:[17,4,1,""],status:[17,4,1,""],time:[17,4,1,""],type:[17,4,1,""],username:[17,4,1,""]},"messages.Probe":{action:[17,4,1,""],time:[17,4,1,""]},"messages.Quit":{action:[17,4,1,""]},"messages.Response":{alert:[17,4,1,""],response:[17,4,1,""],time:[17,4,1,""]},"messages.SendKey":{action:[17,4,1,""],key:[17,4,1,""]},"server.server":{ClientInstance:[20,2,1,""]},"server.server.ClientInstance":{action_handler:[20,3,1,""],add_contact:[20,3,1,""],authenticate:[20,3,1,""],client_disconnect:[20,3,1,""],client_presence:[20,3,1,""],del_contact:[20,3,1,""],encrypt_data:[20,3,1,""],feed_data:[20,3,1,""],get_contacts:[20,3,1,""],get_data:[20,3,1,""],get_filtered_users:[20,3,1,""],get_messages:[20,3,1,""],join:[20,3,1,""],leave:[20,3,1,""],on_msg:[20,3,1,""],probe:[20,3,1,""],send_message:[20,3,1,""],send_response:[20,3,1,""],send_secret_key:[20,3,1,""]},"server.server_gui":{DataMonitor:[21,2,1,""],ServerMainWindow:[21,2,1,""]},"server.server_gui.DataMonitor":{get_data:[21,3,1,""],gotData:[21,4,1,""]},"server.server_gui.ServerMainWindow":{data_handler:[21,3,1,""],feed_data:[21,3,1,""],get_history:[21,3,1,""],on_login:[21,3,1,""],set_filter:[21,3,1,""],show_history:[21,3,1,""],show_users:[21,3,1,""]},"server.server_gui_processor":{ServerGuiProcessor:[22,2,1,""]},"server.server_gui_processor.ServerGuiProcessor":{action_handler:[22,3,1,""],feed_data:[22,3,1,""],get_history:[22,3,1,""],get_users:[22,3,1,""]},"server.server_thread":{PortProperty:[23,2,1,""],ServerEvents:[23,2,1,""],ServerThread:[23,2,1,""]},"server.server_thread.ServerThread":{port:[23,4,1,""],run:[23,3,1,""],send_probe:[23,3,1,""]},"services.Config":{load_config:[24,3,1,""],save_config:[24,3,1,""]},"services.MessageEncoder":{"default":[24,3,1,""]},"services.MessageProcessor":{from_msg:[24,3,1,""]},"services.MessagesDeserializer":{decrypt:[24,3,1,""],deserialize:[24,3,1,""],get_messages:[24,3,1,""],get_msg_lengths:[24,3,1,""],get_msg_list:[24,3,1,""],recv_all:[24,3,1,""],session_key:[24,4,1,""]},"services.SelectableQueue":{close:[24,3,1,""],fileno:[24,3,1,""],get:[24,3,1,""],getpeername:[24,3,1,""],is_not_empty:[24,3,1,""],put:[24,3,1,""]},"test.test_client":{client_create:[26,1,1,""],presence:[26,1,1,""],test_action_handler_probe:[26,1,1,""],test_authenticate:[26,1,1,""],test_disconnect:[26,1,1,""]},"test.test_server":{client_messages:[27,1,1,""],server_create:[27,1,1,""],test_authenticate_200:[27,1,1,""],test_authenticate_402_wrong_pwd:[27,1,1,""],test_authenticate_402_wrong_user:[27,1,1,""],test_authenticate_409_already_connected:[27,1,1,""],test_check_pwd:[27,1,1,""],test_check_pwd_wrong:[27,1,1,""],test_probe:[27,1,1,""]},chat_server:{run_admin:[1,1,1,""]},client:{client:[3,0,0,"-"],client_gui:[4,0,0,"-"],client_gui_processor:[5,0,0,"-"],client_thread:[6,0,0,"-"]},db:{base:[8,0,0,"-"],client:[9,0,0,"-"],client_history:[10,0,0,"-"],contacts:[11,0,0,"-"],messages:[12,0,0,"-"]},log:{log:[15,0,0,"-"],log_config:[16,0,0,"-"]},messages:{AddContact:[17,2,1,""],AdminGetHistory:[17,2,1,""],AdminGetUsers:[17,2,1,""],Authenticate:[17,2,1,""],DelContact:[17,2,1,""],FilterClients:[17,2,1,""],GetContacts:[17,2,1,""],GetMessages:[17,2,1,""],Join:[17,2,1,""],Leave:[17,2,1,""],Msg:[17,2,1,""],Presence:[17,2,1,""],Probe:[17,2,1,""],Quit:[17,2,1,""],Response:[17,2,1,""],SendKey:[17,2,1,""]},server:{server:[20,0,0,"-"],server_gui:[21,0,0,"-"],server_gui_processor:[22,0,0,"-"],server_thread:[23,0,0,"-"]},services:{Config:[24,2,1,""],MessageEncoder:[24,2,1,""],MessageProcessor:[24,2,1,""],MessagesDeserializer:[24,2,1,""],SelectableQueue:[24,2,1,""],serializer:[24,1,1,""]},test:{test_client:[26,0,0,"-"],test_server:[27,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:method","4":"py:attribute"},terms:{"1619529721":[],"1619595326":17,"200":17,"2021":12,"396554":[],"5121322":17,"5131338":17,"5136344":17,"5141358":17,"5146358":17,"5151372":17,"5156379":17,"5161386":17,"5166252":17,"5171268":17,"517626":17,"5181272":17,"576849":12,"6498425":[],"7777":23,"byte":17,"case":24,"class":[3,4,5,6,9,10,11,12,17,20,21,22,23,24],"default":[23,24],"float":[3,4,17],"int":17,"new":[4,21],"public":[3,4,20],"return":[3,4,20,23,24],"static":24,"true":[3,24],"try":24,For:24,The:[],__json__:24,account_nam:3,action:17,action_handl:[3,5,20,22],activ:[],add:20,add_client:9,add_contact:[3,11,17,20],add_log:4,add_messag:12,add_record:10,add_to_contact:4,addcontact:[3,17,20],adding:[3,4],addr:20,address:[1,10,23],admin:22,admin_get_histori:17,admin_get_us:17,admingethistori:[5,17,21,22],admingetus:[5,17,21],after:3,alert:17,all:[21,22,23],allow_nan:24,ani:[3,4,5,20],answer:[3,20],appropri:4,arbitrari:24,arg:[4,6,23,24],argument:[],auth_client:9,authent:[3,4,17,20],avail:24,backend:21,bar:4,base:[3,4,5,6,7,9,10,11,12,13,17,20,21,22,23,24],being:4,between:[3,20],block:24,bodi:[3,4],bool:17,call:24,callabl:[],cancel:4,cancel_profil:4,cfg:4,chang:4,change_search:4,channel:20,chat:[4,20],chat_client:13,chat_serv:13,check:[4,20],check_circular:24,check_pwd:[],cipher:3,classmethod:24,client:[7,10,11,12,13,20,23],client_creat:26,client_disconnect:20,client_gui:[2,13],client_gui_processor:[2,13],client_histori:[7,13],client_id:[10,11],client_login:11,client_messag:27,client_pres:20,client_thread:[2,13],clientguiprocessor:5,clienthistori:10,clienthistorystorag:10,clientinst:20,clientmainwindow:4,clientserverapp:[],clientstorag:9,clientthread:6,close:[3,4,20,24],closeev:4,code:20,commun:3,config:[4,24],configur:4,configure_log:15,conn:[20,24],connect:[3,4,6,20,21,23],constructor:[],contact:[3,4,7,9,13,17,20,21],contact_select:4,contactstorag:11,could:24,creat:[3,20,23],credenti:20,data:[3,4,5,20,21,22,24],data_handl:[4,21],dataclass:[3,4,5,20,21,22],datamonitor:21,datetim:12,debug:15,decl_api:[9,10,11,12],decrypt:24,def:24,del_contact:[3,4,11,17,20],delcontact:[3,4,17,20],delet:[3,4],deseri:24,dict:20,disconnect:[3,20],doesn:20,element:[4,21],els:24,empti:24,encod:24,encrypt:[3,20],encrypt_data:20,ensure_ascii:24,event:[1,23],event_dict:16,exampl:24,except:24,exist:[4,20],fals:[9,17,20,24],feed_data:[3,4,5,20,21,22],file:4,filenam:16,fileno:24,filter:[4,20,21],filter_cli:[9,17],filtercli:[4,17,20],find:20,find_client:[],format:4,frame:4,free:24,from:[3,4,5,12,20,21,22,24],from_:17,from_id:12,from_msg:24,full:24,func:24,get:[3,20,21,22,24],get_al:9,get_chat_msg:12,get_client:9,get_contact:[3,11,17,20],get_data:[3,20,21],get_filter_us:4,get_filtered_us:20,get_from_owner_messag:12,get_histori:[5,10,21,22],get_messag:[3,17,20,24],get_msg_length:24,get_msg_list:24,get_socket:24,get_to_owner_msg_from_tim:12,get_to_user_messag:12,get_us:[5,22],getcontact:[3,4,17,20,21],getmessag:[3,4,17,20],getpeernam:24,gotdata:21,gui:[3,21,22],has:3,hide:4,his:20,histori:[4,17,21,22],ignor:24,immedi:24,implement:24,indent:24,index:13,inform:20,initi:6,instanc:[21,23],interv:23,invok:[],ip_address:10,is_admin:9,is_contact:4,is_not_contact:4,is_not_empti:24,item:[21,24],iter:24,its:24,join:[3,17,20],json:24,jsonencod:24,just:20,kei:[3,4,17,20],keyword:[],kwarg:[4,6,9,10,11,12,23,24],leav:[3,17,20],let:24,leverag:24,lib:12,like:24,list:[3,4,20,21,22,24],listen:23,load:4,load_config:[4,24],local:4,localhost:23,log:13,log_config:[13,14],log_default:16,log_level:15,logger:16,logger_nam:16,login:[4,9,17,22],loop:[6,23],mai:[],main:[4,6,23],mask:[4,20,21],messag:[3,4,5,7,9,13,20,21,22],messageencod:24,messageprocessor:24,messagesdeseri:24,messagestorag:12,method:[21,24],method_nam:16,modul:13,most:24,msg:[3,4,5,12,17,20,22,24],name:3,necessari:24,neg:24,non:24,none:[3,5,22,24],number:24,obj:24,object:[3,5,9,10,11,12,17,20,21,22,23,24],obtain:24,offlin:17,on_auth:4,on_login:21,on_msg:[3,4,20],one:[4,21,24],onlin:20,option:24,orm:[9,10,11,12],otherwis:24,over:23,overrid:[],owner:[10,11,12],owner_id:11,packag:13,page:13,param:[3,4,5,20,21,22],parent:21,pass:24,password:[3,9,17,20],path:24,pathlib:24,pattern:[9,17],ping:23,port:[1,23],portproperti:23,presenc:[3,17,20,26],probe:[17,20],proc:16,process:[3,4,5,20,21,22],processor:15,profil:4,public_kei:17,put:[21,22,24],put_socket:24,pyqt5:[4,21],pyqt:21,python39:12,qcloseev:[],qmainwindow:[4,21],qobject:21,qtcore:21,qtwidget:[4,21],queue:[4,21,22,24],quit:17,rais:24,receiv:4,recipi:[12,20],recv_al:24,remov:24,repres:[],represent:24,request:[3,4,20,21],respect:[],respons:[3,17,20],response_processor:3,result:[3,17],room:[3,17],room_nam:17,run:[6,23],run_admin:1,run_client:13,save:4,save_config:24,save_profil:4,search:13,second:24,select:4,selectablequeu:[4,5,21,22,23,24],selector:[6,23],self:24,send:[3,4,5,20,21,23],send_kei:3,send_messag:[3,4,20],send_prob:23,send_respons:20,send_secret_kei:20,sender:[3,4],sendkei:[17,20],sent:4,separ:24,sequenti:[],serial:24,serializ:24,server:[3,4,5,13],server_cr:27,server_gui:[13,19],server_gui_processor:[13,19],server_thread:[13,19],serverev:23,serverguiprocessor:22,servermainwindow:21,serverthread:23,servic:[4,5,13,21,22,23],session:[5,9,10,11,12,20,22],session_kei:[3,24],set:[20,21],set_filt:21,set_statu:9,show:[4,21],show_contact:4,show_filter_us:4,show_histori:21,show_us:21,skipkei:24,slot:24,socket:23,sort_kei:24,sourc:[1,3,4,5,6,9,10,11,12,15,16,17,20,21,22,23,24,26,27],specif:[4,20,21,22,23],sq_admin:[21,23],sq_client:4,sq_gui:[3,4,5,21,22,23],sqlalchemi:[9,10,11,12],standard:[],start:[6,23],statu:[3,4,9,17,20],store:[20,21],str:[4,12,17,21],string:4,subclass:24,submodul:13,support:24,taken:[],target:[3,22],test:13,test_action_handler_prob:26,test_authent:26,test_authenticate_200:27,test_authenticate_402_wrong_pwd:27,test_authenticate_402_wrong_us:27,test_authenticate_409_already_connect:27,test_check_pwd:27,test_check_pwd_wrong:27,test_client:[13,25],test_disconnect:26,test_prob:27,test_serv:[13,25],text:[3,4,17,20,21],thi:[3,4,24],thread:[6,23],through:[4,5],time:[3,4,17,24],timeout:24,to_id:12,toggle_login_widget:4,toggle_profil:4,tupl:[4,6,17,21],type:[3,4,5,17,20,21,22],typeerror:24,until:24,updat:[4,21],update_chat:4,user:[3,4,6,12,17,20,21,22],usernam:[3,4,17,21,22],when:[10,12,21],where:21,window:4,within:24,you:24},titles:["chat_client module","chat_server module","client package","client.client module","client.client_gui module","client.client_gui_processor module","client.client_thread module","db package","db.base module","db.client module","db.client_history module","db.contacts module","db.messages module","Welcome to ClientServerApps\u2019s documentation!","log package","log.log module","log.log_config module","messages module","run_clients module","server package","server.server module","server.server_gui module","server.server_gui_processor module","server.server_thread module","services module","test package","test.test_client module","test.test_server module"],titleterms:{base:8,chat_client:0,chat_serv:1,client:[2,3,4,5,6,9],client_gui:4,client_gui_processor:5,client_histori:10,client_thread:6,clientserverapp:13,contact:11,content:[2,7,13,14,19,25],document:13,indic:13,log:[14,15,16],log_config:16,messag:[12,17],modul:[0,1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,20,21,22,23,24,25,26,27],packag:[2,7,14,19,25],run_client:18,server:[19,20,21,22,23],server_gui:21,server_gui_processor:22,server_thread:23,servic:24,submodul:[2,7,14,19,25],tabl:13,test:[25,26,27],test_client:26,test_serv:27,welcom:13}})