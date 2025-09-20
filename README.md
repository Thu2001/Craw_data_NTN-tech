Dự Án Data Pipeline Thu Thập Dữ Liệu Sản Phẩm
Dự án này là một quy trình tự động (data pipeline) được xây dựng để thu thập dữ liệu sản phẩm từ các trang web thương mại điện tử, xử lý và lưu trữ chúng vào cơ sở dữ liệu PostgreSQL để phân tích.

1. Công Nghệ Sử Dụng
   Web Scraping/Crawling:

Python: Ngôn ngữ lập trình chính.

Scrapy: Framework mạnh mẽ để xây dựng các spider thu thập dữ liệu web.

Beautiful Soup & Requests: Các thư viện phổ biến để trích xuất dữ liệu từ HTML.

Xử lý Dữ liệu:

Pyspark: để sử lý dữ liệu lớn

Pandas: Thư viện Python để làm sạch, biến đổi và tổng hợp dữ liệu.

Cơ sở Dữ liệu:

PostgreSQL: Hệ quản trị cơ sở dữ liệu quan hệ, nơi lưu trữ dữ liệu đã được xử lý.

Tự động hóa:

Docker (Tùy chọn): Đóng gói ứng dụng để dễ dàng triển khai.

Apache Airflow (Tùy chọn): Lên lịch và quản lý luồng công việc tự động.

2. Mô Hình Cơ Sở Dữ Liệu
   Dữ liệu sản phẩm được lưu trữ trong cơ sở dữ liệu PostgreSQL theo mô hình đã được chuẩn hóa để tối ưu hóa hiệu suất và giảm thiểu dư thừa.

Bảng Categories (Loại Sản Phẩm)
Lưu trữ thông tin về các loại sản phẩm.

category_id (PRIMARY KEY, INT)

category_name (VARCHAR)

Bảng Brands (Thương Hiệu)
Lưu trữ thông tin về các thương hiệu.

brand_id (PRIMARY KEY, INT)

brand_name (VARCHAR)

Bảng Products (Sản Phẩm)
Lưu trữ thông tin chi tiết của từng sản phẩm.

product_id (PRIMARY KEY, INT)

product_name (VARCHAR)

description (TEXT)

download_link (VARCHAR)

category_id (FOREIGN KEY, INT): Liên kết tới bảng Categories.

brand_id (FOREIGN KEY, INT): Liên kết tới bảng Brands.

3. Quy Trình Hoạt Động
   Thu Thập (Extraction): Các script web scraping sẽ tự động truy cập các trang web được chỉ định, trích xuất dữ liệu thô (tên sản phẩm, mô tả, thương hiệu, loại sản phẩm, v.v.).

Xử lý (Transformation): Dữ liệu thô được đưa qua các bước làm sạch:

Loại bỏ ký tự không mong muốn.

Chuẩn hóa tên thương hiệu và loại sản phẩm.

Phân loại sản phẩm và thương hiệu để tạo các khóa ngoại.

Nạp (Loading): Dữ liệu đã xử lý được đưa vào các bảng tương ứng trong cơ sở dữ liệu PostgreSQL. Các script sẽ kiểm tra và cập nhật các bản ghi hiện có hoặc thêm mới.

4. Hướng Dẫn Cài Đặt và Sử Dụng
   Yêu cầu: Đảm bảo bạn đã cài đặt Python 3 và PostgreSQL trên hệ thống.

Cài đặt thư viện:

Bash

pip install scrapy beautifulsoup4 requests pandas psycopg2-binary
Thiết lập cơ sở dữ liệu: Chạy các câu lệnh SQL để tạo các bảng Categories, Brands, và Products theo mô hình đã mô tả ở trên.

Chạy dự án: Chạy các script thu thập và xử lý dữ liệu.

5. Đóng Góp Ý Kiến
   Mọi đóng góp để cải thiện dự án đều được hoan nghênh.
