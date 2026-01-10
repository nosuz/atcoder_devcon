package {{content.contest}};

/*
* {{content.title}}
* {{content.url}}
*
* Test command: gradle test --tests {{content.Name}}Test
* Test command: gradle test --tests {{content.Name}}Test.sample1
*/

import java.util.Scanner;

public class {{content.Name}} {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int M = sc.nextInt(); //
        int N = sc.nextInt(); //

        sc.close();

        System.out.println("Hello World\n");
    }
}
