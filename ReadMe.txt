Commands:


1. For configuring the application on MySQL Alchemy:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@mysql/socialnetwork'

2. Creating the first Database:
docker run -p 3306:3306 --name mysqlserver -e MYSQL_ROOT_PASSWORD=root -d mysql:5.6

3. For accessing MySQL:
docker exec -it mysqlserver mysql -uroot -p
Using this, we can create the database, create the tables and populate the initial data.

4. Now build the application containers:
docker build -t fb .
docker build -t fb2 .

5. Link the database containers and the application containers.
docker run --link mysqlserver:mysql --link mysqlserver2:mysql2 -p 8001:5000 fb
docker run --link mysqlserver:mysql --link mysqlserver2:mysql2 -p 8003:5000 fb2