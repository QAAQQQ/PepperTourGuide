-module(server).
-export([main/1]).

main(_) ->
  inets:start(),
  {ok, Pid} = inets:start(httpd, [
    {port, 5550},
    {server_name,"httpd_test"},
    {server_root,"/home/pi/web_server"},
    {document_root,"/home/pi/web_server"},
    {bind_address, {192, 168, 0, 103}},
    {modules, [handler]}
  ]),
  {ok, Pid},
  register(server_a, self()),
  loop(#{floor => "6", saying => "", pos => "20.0;17.0"}).

loop(Map=#{floor := Floor, saying := Saying, pos := Pos}) ->
  Next = receive
    {put_say, Say} -> Map#{saying => Say};
    {put_floor, NFloor} -> Map#{floor => NFloor};
    {put_pos, NPos} -> Map#{pos => NPos};
    {get_say, From} -> From!{saying, Saying}, Map;
    {get_floor, From} -> From!{floor, Floor}, Map;
    {get_pos, From} -> From!{pos, Pos}, Map
  end,
  loop(Next).
