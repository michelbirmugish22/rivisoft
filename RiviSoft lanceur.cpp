//#include<iostream>
//#include <cstdlib>
//using namespace std;
//
//int main(){
//	system("py manage.py runserver");
//	const char* url = "https://www.google.com";
//    //system(("xdg-open "+string(url)).c_str()); //Sur Linix
//    system(("start "+string(url)).c_str());
//	return 0;
//}

#include <windows.h>

int main() {
	HINSTANCE hInstance = ShellExecute(NULL,NULL,"http://127.0.0.1:8000",NULL,NULL,SW_SHOWDEFAULT);
	system("py manage.py runserver");
  
	  if (hInstance == NULL) {
	    MessageBox(NULL, "Échec de l'ouverture de Riviera SOFT", "Erreur", MB_OK);
	  }

  return 0;
}
