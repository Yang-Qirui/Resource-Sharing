#### Data

This directory is used for saving data for analysis.

* figure directory: use `src/batch_test.py` to run test, and the visualized result will be store in this directory. `total.png` show the average time and fit curve for those testcases in different directories in matrix directory, and other png file show the executing time for testcases which are in the same sub directory of matrix directory, in scatter form.
* matrix directory: use `src/gen_test.py` to generate testcases (you can custom the m,n,c in this python script). This directory stores many testcases in matrix form. Every sub directory store testcases in matrix form which satisfy the condition that the row size of matrix equal to m, column size equal to n, and the number of operation equal to c. 