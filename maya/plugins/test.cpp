#include <iostream>

using namespace std;

int main()
{
	int i;
	int j;
	for(i=0; i<10; i++)
	{
		for(j=0; j<10; j++)
		{
			if(i == j)
			{
				cout << "*";
			}
			else
			{
				cout << " ";
			}
		}
		cout << endl;
	}

}
