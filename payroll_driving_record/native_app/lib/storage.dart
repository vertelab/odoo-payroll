import 'package:shared_preferences/shared_preferences.dart';

Future<SharedPreferences> shared = SharedPreferences.getInstance();

var session;
var employee_id;
String? url = '';
String? db = '';
String? user = '';
String? passwd = '';
bool? recall = false;

DateTime? date = DateTime.now();
int? destination;
bool? business = true;
String? odo_start = '';
String? odo_stop = '';
String? note = '';
