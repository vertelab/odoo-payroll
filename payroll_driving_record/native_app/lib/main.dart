//  Driving Record app by Vertel AB
//  Code written by Robin Calvin

//import 'dart:developer';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_form_builder/flutter_form_builder.dart';
import 'package:form_builder_validators/form_builder_validators.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:odoo_rpc/odoo_rpc.dart';
import 'package:textfield_search/textfield_search.dart';
import 'package:string_validator/string_validator.dart';
import 'package:intl/intl.dart';

import 'storage.dart' as storage;

// ignore_for_file: unused_local_variable

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Driving Record',
        theme: ThemeData(
          primarySwatch: Colors.purple,
        ),
        home: MyAppContextExtension());
  }
}

class MyAppContextExtension extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driving Record'),
        actions: [
          PopupMenuButton(
              icon: Icon(Icons.menu),
              onSelected: ((value) => showAbout(context)),
              itemBuilder: ((context) => [
                    PopupMenuItem(
                      value: 1,
                      child: Row(
                          children: const [Icon(Icons.info_outline_rounded, color: Colors.black45), Text(' About')]),
                    )
                  ]))
        ],
      ),
      body: MyUi(),
      resizeToAvoidBottomInset: false, // Makes the navigation-bar avoid the keyboard
    );
  }
}

class MyUi extends StatefulWidget {
  MyUi({Key? key}) : super(key: key);
  final products = ['test', 'mer test'];

  @override
  State<MyUi> createState() => _MyUiState();
}

class _MyUiState extends State<MyUi> {
  final GlobalKey<FormState> formKey = GlobalKey<FormState>();
  static bool? checkedValue = false;
  bool? newValue;
  String errormsg = '';
  String createmsg = '';
  int _selectedIndex = 0;
  List lines = [
    {'date': '2022-01-01', 'type': '', 'odometer_start': '', 'odometer_stop': '', 'length': ''},
  ];

  void _onItemTapped(int index) {
    if (storage.session is OdooClient) {
      if (index > 0) {
        setState(() => _selectedIndex = index);
      } else if (index == 0) {
        showDialog(
            context: context,
            builder: (ctx) => AlertDialog(
                  title: const Text('Log out?'),
                  content: const Text('Press OK to disconnect and return to the login tab.'),
                  actions: <Widget>[
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, 'Cancel'),
                      child: const Text('Cancel', style: TextStyle(fontSize: 20)),
                    ),
                    TextButton(
                      onPressed: () {
                        Navigator.pop(ctx, 'OK');
                        if (storage.session is OdooClient) {
                          storage.session.close();
                          storage.session = String;
                        }
                        setState(() => _selectedIndex = 0);
                      },
                      child: const Text('OK', style: TextStyle(fontSize: 20)),
                    ),
                  ],
                ));
      }
    } else {}
  }

  @override
  Widget build(BuildContext context) {
    final formKey = GlobalKey<FormBuilderState>();
    final newJourneyKey = GlobalKey<FormBuilderState>();

    TextEditingController destController = TextEditingController();

    @override
    void dispose() {
      // Clean up the controller when the widget is removed from the
      // widget tree.
      destController.dispose();
      super.dispose();
    }

    List<Widget> pages = <Widget>[
      // Login page
      FormBuilder(
          key: formKey,
          child: SingleChildScrollView(
            child: Column(children: [
              const SizedBox(height: 7), // Space between fields
              FormBuilderTextField(
                style: const TextStyle(fontSize: 17),
                name: 'field1',
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Server url',
                  hintText: 'Server url',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.http),
                ),
                onChanged: (field1_text) {
                  // Stores input temporary so the field doesn't reset when setState() is called
                  storage.url = field1_text;
                },
                initialValue: storage.url,
                validator: FormBuilderValidators.url(
                  errorText: 'Please enter a valid url',
                ),
              ),
              const SizedBox(height: 6),
              FormBuilderTextField(
                style: const TextStyle(fontSize: 17),
                name: 'field2',
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Database name',
                  hintText: 'Database name',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.storage),
                ),
                onChanged: (field2_text) {
                  storage.db = field2_text;
                },
                initialValue: storage.db,
                validator: FormBuilderValidators.required(
                  errorText: 'Please enter the database name',
                ),
              ),
              const SizedBox(height: 6),
              FormBuilderTextField(
                style: const TextStyle(fontSize: 17),
                name: 'field3',
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'User name',
                  hintText: 'User name',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
                onChanged: (field3_text) {
                  storage.user = field3_text;
                },
                initialValue: storage.user,
                validator: FormBuilderValidators.required(
                  errorText: 'Please enter your username',
                ),
              ),
              const SizedBox(height: 6),
              FormBuilderTextField(
                style: const TextStyle(fontSize: 17),
                name: 'field4',
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Password',
                  hintText: 'Password',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.password),
                ),
                obscureText: true,
                onChanged: (field4_text) {
                  storage.passwd = field4_text;
                },
                initialValue: storage.passwd,
                validator: FormBuilderValidators.required(
                  errorText: 'Please enter your password',
                ),
              ),
              CheckboxListTile(
                title: const Text("Remember options"),
                value: checkedValue,
                onChanged: (bool? newValue) {
                  setState(() {
                    checkedValue = newValue;
                  });
                },
                controlAffinity: ListTileControlAffinity.trailing,
              ),
              ElevatedButton(
                style: const ButtonStyle(),
                onPressed: () {
                  formKey.currentState?.save();
                  if (formKey.currentState!.validate()) {
                    final formData = formKey.currentState?.value;

                    storage.shared.then((stor) {
                      stor.setString('url', formData?['field1']);
                      stor.setString('db', formData?['field2']);
                      stor.setString('user', formData?['field3']);
                      stor.setString('passwd', formData?['field4']);
                      stor.setBool('recall', checkedValue as bool);
                    });

                    var session =
                        odoo_login(formData?['field1'], formData?['field2'], formData?['field3'], formData?['field4'])
                            .then((session) {
                      if (session is String) {
                        setState(() => errormsg = session); // Show error message
                        Future.delayed(
                          const Duration(seconds: 3),
                          () => setState(() => errormsg = ''), // Clear error message after 3 seconds
                        );
                      } else if (session is OdooClient) {
                        odoo_getEmployeeId(session).then((employee_id) {
                          if (employee_id is String) {
                            setState(() => errormsg = employee_id); // Show error message
                            Future.delayed(const Duration(seconds: 3), () => setState(() => errormsg = ''));
                          } else {
                            // storage.employee_id = employee_id;
                            odoo_getDrivingRecords(session, employee_id).then((data) {
                              setState(() {
                                lines = data;
                                _selectedIndex = 1; // Activate second tab ('New trip')
                              });
                              storage.session = session;
                              storage.employee_id = employee_id;
                            });
                          }
                        });
                      }
                    });
                  }
                },
                child: const Text(
                  'Login',
                  style: TextStyle(fontSize: 20),
                ),
              ),
              Text(
                errormsg,
                style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 18),
              ),
            ]),
          )),

      FormBuilder(
          key: newJourneyKey,
          child: SingleChildScrollView(
            child: Column(children: [
              const SizedBox(height: 7),
              FormBuilderDateTimePicker(
                style: const TextStyle(fontSize: 17),
                name: 'date',
                inputType: InputType.date,
                format: DateFormat('yyyy-MM-dd'),
                resetIcon: const Icon(null),
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Date',
                  hintText: 'Date',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.date_range),
                ),
                onChanged: (date) {
                  storage.date = date;
                },
                initialValue: storage.date,
              ),
              const SizedBox(height: 5),
              TextFieldSearch(
                label: 'Destination!',
                controller: destController,
                future: () {
                  return odoo_getDestPartner(storage.session, destController.text);
                },
                getSelectedValue: (selected) {
                  storage.destination = selected.value;
                },
                itemsInView: 100,
                minStringLength: 1,
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Destination',
                  hintText: 'Destination',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.drive_eta),
                ),
              ),
              const SizedBox(height: 5),
              FormBuilderSwitch(
                name: 'type',
                title: const Text(
                  'Business',
                  style: TextStyle(fontSize: 17),
                ),
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Type',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.business_center),
                  contentPadding: EdgeInsets.symmetric(vertical: 6),
                ),
                initialValue: storage.business,
                onChanged: (business) {
                  storage.business = business;
                },
              ),
              const SizedBox(height: 5),
              FormBuilderTextField(
                name: 'odometer_start',
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Odometer start',
                  hintText: 'Odometer start',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.start),
                ),
                onChanged: (odo_start) {
                  storage.odo_start = odo_start;
                },
                initialValue: storage.odo_start,
                validator: FormBuilderValidators.required(
                  errorText: 'Please enter the odometer number for the start of the trip',
                ),
              ),
              const SizedBox(height: 5),
              FormBuilderTextField(
                name: 'odometer_stop',
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Odometer stop',
                  hintText: 'Odometer stop',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.stop_circle),
                ),
                onChanged: (odo_stop) {
                  storage.odo_stop = odo_stop;
                },
                initialValue: storage.odo_stop,
                validator: FormBuilderValidators.required(
                  errorText: 'Please enter the odometer number for the end of the trip',
                ),
              ),
              const SizedBox(height: 5),
              FormBuilderTextField(
                style: const TextStyle(fontSize: 17),
                name: 'note',
                decoration: const InputDecoration(
                  floatingLabelBehavior: FloatingLabelBehavior.always,
                  labelText: 'Note',
                  hintText: 'Note',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.edit_note),
                ),
                onChanged: (note) {
                  storage.note = note;
                },
                initialValue: storage.note,
              ),
              ElevatedButton(
                child: const Text(
                  'Create',
                  style: TextStyle(fontSize: 20),
                ),
                onPressed: () {
                  newJourneyKey.currentState?.save();
                  if (newJourneyKey.currentState!.validate()) {
                    final formData = newJourneyKey.currentState?.value;
                    //           print(destController.text);
                    odoo_createDrivingRecord(storage.session, formData!).then((record) {
                      if (record is String) {
                        showError(context, record, 'OK');
                      } else {
                        odoo_getDrivingRecords(storage.session, storage.employee_id).then((data) {
                          setState(() {
                            lines = data;
                            storage.date = DateTime.now();
                            storage.destination = null;
                            storage.business = true;
                            storage.odo_start = '';
                            storage.odo_stop = '';
                            storage.note = '';
                            createmsg = 'Your trip has been added to the list';
                          });
                          Future.delayed(const Duration(seconds: 3), () => setState(() => createmsg = ''));
                        });
                      }
                    });
                  }
                },
              ),
              Text(
                createmsg,
                style: TextStyle(color: Colors.green.shade700, fontWeight: FontWeight.bold, fontSize: 18),
              ),
            ]),
          )),

      Scaffold(
        // Journey List page
        body: DataTable2(
          columnSpacing: 0,
          horizontalMargin: 7,
          showBottomBorder: true,
          headingRowColor: MaterialStateProperty.resolveWith((headingColor) => Colors.grey[200]),
          columns: const <DataColumn2>[
            DataColumn2(
              label: Icon(null),
              //size: ColumnSize.S,
              fixedWidth: 35,
            ),
            DataColumn2(
              label: Text(
                'Date',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              size: ColumnSize.L,
            ),
            DataColumn2(
                label: Text(
                  'Type',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                size: ColumnSize.L),
            DataColumn2(
              label: Text(
                'Start',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            DataColumn2(
              label: Text(
                'Stop',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            DataColumn2(
              label: Text(
                'Length',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ],
          rows: <DataRow2>[
            for (var line in lines.reversed)
              DataRow2(cells: <DataCell>[
                DataCell(Icon(Icons.drive_eta)),
                DataCell(Text(line['date'].toString().substring(2))),
                DataCell(Text(toBeginningOfSentenceCase(line['type']) as String)),
                DataCell(Text(line['odometer_start'].toString())),
                DataCell(Text(line['odometer_stop'].toString())),
                DataCell(Text(line['length'].toString() + ' km')),
              ])
          ],
          //-------------
        ),
      )
    ];
    return Scaffold(
      body: IndexedStack(index: _selectedIndex, children: pages),
      bottomNavigationBar: BottomNavigationBar(
        onTap: _onItemTapped,
        currentIndex: _selectedIndex,
        backgroundColor: Colors.purple,
        selectedItemColor: Colors.white,
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.mobile_friendly),
            activeIcon: Icon(Icons.login),
            label: 'Login',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'New trip',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.view_list_rounded),
            label: 'Journey list',
          ),
        ],
      ),
    );
  }

  @override
  void initState() {
    super.initState();

    storage.shared.then((stor) {
      if (stor.containsKey('recall')) {
        if (stor.getBool('recall') == true) {
          setState(() {
            storage.url = stor.getString('url');
            storage.db = stor.getString('db');
            storage.user = stor.getString('user');
            storage.passwd = stor.getString('passwd');
            storage.note = stor.getString('note');
            checkedValue = stor.getBool('recall');
          });
        }
      }
    });
  }

  Future odoo_login(String server, String database, String user, String password) async {
    final client;

    Map<String, Object> options = {
      'protocols': ['http', 'https'],
      'require_protocol': true,
    };

    var httptest = 'http://$server';
    if (isURL(httptest, options)) {
      server = 'http://$server';
    }
    if (isURL(server, options)) {
      client = OdooClient(server);
    } else {
      return 'Server is not an URL';
    }

    try {
      final session = await client.authenticate(database, user, password);
      return client;
    } on OdooException catch (e) {
      client.close();
      if (e.message.contains('exceptions.AccessDenied')) {
        return 'Access Denied';
      } else if (e.message.contains('psycopg2.OperationalError')) {
        return 'Database Error';
      }
    } on Exception catch (err) {
      return err.toString();
    }
  }
}

Future odoo_getEmployeeId(OdooClient client) async {
  var userid = client.sessionId?.userId;
  try {
    var user = await client.callKw({
      'model': 'res.users',
      'method': 'search_read',
      'args': [],
      'kwargs': {
        'domain': [
          ['id', '=', userid]
        ],
        'fields': ['employee_id'],
        'limit': 1,
      },
    });
    if (user[0]['employee_id'] == false) {
      client.close();
      return 'User has no employee ID';
    } else {
      return user[0]['employee_id'][0];
    }
  } on Exception catch (e) {
    return 'Error fetching user data';
  }
}

Future<List?> odoo_getDestPartner(OdooClient client, searchstring) async {
  try {
    var destpartner = await client.callKw({
      'model': 'res.partner',
      'method': 'search_read',
      'args': [],
      'kwargs': {
        'domain': [
          ['name', 'ilike', searchstring]
        ],
        'fields': ['name'],
        'limit': 100,
      },
    });

    List res_list = [];
    //storage.res_id_list = [];
    for (var data in destpartner) {
      if (data is Map) {
        res_list.add(dropDownItem(data['name'], data['id']));
      }
    }

    return res_list;
  } on Exception catch (e) {
    return [];
  }
}

class dropDownItem {
  String label;
  dynamic value;

  dropDownItem(this.label, this.value) {}
}

Future odoo_getDrivingRecords(OdooClient client, employee_id) async {
  try {
    var lines = await client.callKw({
      'model': 'driving.record.line',
      'method': 'search_read',
      'args': [],
      'kwargs': {
        'domain': [
          ['employee_id', '=', employee_id]
        ],
        'fields': [
          'date',
          'type',
          'odometer_start',
          'odometer_stop',
          'length',
          'note',
        ],
        'limit': 250,
      },
    });

    return lines;
  } on OdooException catch (e) {
//      client.close();
    if (e.message.contains('builtins.ValueError')) {
      return 'ValueError';
    }
  } on Exception catch (e) {
    return;
  }
}

Future odoo_createDrivingRecord(OdooClient client, Map formData) async {
  try {
    var date, type, odometer_start, odometer_stop, note;

    if (formData['date'] is DateTime) {
      date = formData['date'].toString().split(' ')[0];
    }
    if (formData['type'] == true) {
      type = 'business';
    } else {
      type = 'private';
    }
    odometer_start = formData['odometer_start'];
    odometer_stop = formData['odometer_stop'];
    if (formData['note'] == null) {
      note = '';
    } else {
      note = formData['note'];
    }

    var result = await client.callKw({
      'model': 'driving.record.line',
      'method': 'add_driving_line',
      'args': [date, odometer_start, odometer_stop, note, type, storage.employee_id, storage.destination],
      'kwargs': {},
    });

    return result;
  } on OdooException catch (e) {
//      client.close();

    if (e.message.contains('builtins.ValueError')) {
      return 'ValueError';
    } else if (e.message.contains('odoo.exceptions.ValidationError:')) {
      return parseErrorMsg(e.message);
    } else {
      return 'An unknown error occurred';
    }
  }
}

String parseErrorMsg(String input) {
  const startWord = 'odoo.exceptions.ValidationError:';
  const endWord = ', message:';

  final startIndex = input.indexOf(startWord);
  final endIndex = input.indexOf(endWord, startIndex + startWord.length);

  final String output = input.substring(startIndex + startWord.length, endIndex);
  return output.trim();
}

void showError(BuildContext context, String msg, String button) {
  showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
            title: const Text('Fel'),
            content: Text(msg, style: const TextStyle(fontSize: 19)),
            actions: <Widget>[
              TextButton(
                onPressed: () => Navigator.pop(ctx, 'OK'),
                child: Text(button, style: const TextStyle(fontSize: 20)),
              ),
            ],
          ));
}

void showAbout(BuildContext context) {
  showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
            // title: const Text('About'),
            content: Wrap(alignment: WrapAlignment.center, children: [
              const Text('Driving Record v1.0', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600)),
              const Text('\u00a9 2022 Vertel AB'),
              Image.asset('assets/images/vertel_logo.png'),
              const Text(' '),
              const Center(
                  child: Text(
                'Code & design',
                style: TextStyle(fontSize: 19, fontWeight: FontWeight.w600),
              )),
              const Center(child: Text('\nMobile app:\n', style: TextStyle(fontWeight: FontWeight.w600))),
              const Text('Robin Calvin\n', style: TextStyle(fontSize: 19)),
              const Center(child: Text('Odoo module:\n', style: TextStyle(fontWeight: FontWeight.w600))),
              const Center(child: Text('Victor Ekström', style: TextStyle(fontSize: 19))),
              const Center(child: Text('Björn Hayer', style: TextStyle(fontSize: 19))),
              const Center(child: Text('Anders Wallenquist', style: TextStyle(fontSize: 19))),
            ]),
            actions: <Widget>[
              TextButton(
                onPressed: () => Navigator.pop(ctx, 'OK'),
                child: const Text('OK', style: TextStyle(fontSize: 20)),
              ),
            ],
          ));
}
