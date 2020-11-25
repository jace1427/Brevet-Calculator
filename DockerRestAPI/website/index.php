<html>
    <head>
        <title>Brevets DB</title>
    </head>

    <body>
        <h1>List of Times (JSON)</h1>
        <ul>
            <?php
            $json = file_get_contents('http://brevets/listAll');
            echo $json;
            ?>
        </ul>

        <h1>List of Open Times (CSV)</h1>
        <ul>
            <?php
            $json = file_get_contents('http://brevets/listAll/csv');
            echo $json;
            ?>
        </ul>
    </body>
</html>
