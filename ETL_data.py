import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import logging
import re

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ETLProcessor:
    def __init__(self, csv_file_path, db_connection_string):
        """
        Khởi tạo ETL Processor
        :param csv_file_path: Đường dẫn đến file CSV
        :param db_connection_string: Chuỗi kết nối đến PostgreSQL
        """
        self.csv_file_path = csv_file_path
        self.db_connection_string = db_connection_string
        self.df = None
        self.categories_df = None
        self.brands_df = None
        self.products_df = None
        
    def extract(self):
        """
        Bước Extract: Đọc dữ liệu từ file CSV
        """
        try:
            logger.info(f"Đang đọc file CSV từ: {self.csv_file_path}")
            self.df = pd.read_csv(self.csv_file_path)
            logger.info(f"Đọc thành công. Tổng số dòng: {len(self.df)}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi đọc file CSV: {str(e)}")
            return False
    
    def transform(self):
        """
        Bước Transform: Làm sạch và biến đổi dữ liệu
        """
        try:
            logger.info("Bắt đầu quá trình biến đổi dữ liệu")
            
            # Tạo bảng Categories
            self.categories_df = self.df[['category_id', 'category_name']].drop_duplicates()
            logger.info(f"Tạo bảng Categories với {len(self.categories_df)} bản ghi")
            
            # Tạo bảng Brands
            self.brands_df = self.df[['brand_id', 'brand_name']].drop_duplicates()
            logger.info(f"Tạo bảng Brands với {len(self.brands_df)} bản ghi")
            
            # Tạo bảng Products
            product_columns = ['product_id', 'product_name', 'description', 'download_link', 'category_id', 'brand_id']
            self.products_df = self.df[product_columns].copy()
            
            # Làm sạch dữ liệu cho bảng Products
            # Xử lý giá trị null
            self.products_df['description'] = self.products_df['description'].fillna('Không có mô tả')
            self.products_df['download_link'] = self.products_df['download_link'].fillna('')
            
            # Chuẩn hóa tên sản phẩm (viết hoa chữ cái đầu)
            self.products_df['product_name'] = self.products_df['product_name'].apply(
                lambda x: x.title() if isinstance(x, str) else x
            )
            
            # Kiểm tra và làm sạch các link không hợp lệ
            def clean_link(link):
                if pd.isna(link) or link == '':
                    return ''
                # Kiểm tra nếu link bắt đầu với http hoặc https
                if isinstance(link, str) and not link.startswith(('http://', 'https://')):
                    return f'https://{link}'
                return link
            
            self.products_df['download_link'] = self.products_df['download_link'].apply(clean_link)
            
            logger.info(f"Tạo bảng Products với {len(self.products_df)} bản ghi")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi trong quá trình biến đổi dữ liệu: {str(e)}")
            return False
    
    def load(self):
        """
        Bước Load: Tải dữ liệu đã biến đổi lên PostgreSQL
        """
        try:
            # Kết nối đến PostgreSQL
            engine = create_engine(self.db_connection_string)
            logger.info("Kết nối đến PostgreSQL thành công")
            
            # Tải dữ liệu lên database
            with engine.begin() as connection:
                # Tải Categories
                self.categories_df.to_sql(
                    'categories', 
                    connection, 
                    if_exists='replace', 
                    index=False,
                    method='multi'
                )
                logger.info("Đã tải xong bảng Categories")
                
                # Tải Brands
                self.brands_df.to_sql(
                    'brands', 
                    connection, 
                    if_exists='replace', 
                    index=False,
                    method='multi'
                )
                logger.info("Đã tải xong bảng Brands")
                
                # Tải Products
                self.products_df.to_sql(
                    'products', 
                    connection, 
                    if_exists='replace', 
                    index=False,
                    method='multi'
                )
                logger.info("Đã tải xong bảng Products")
            
            logger.info("Hoàn thành quá trình tải dữ liệu lên PostgreSQL")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi tải dữ liệu lên PostgreSQL: {str(e)}")
            return False
    
    def run_etl(self):
        """
        Chạy toàn bộ quy trình ETL
        """
        logger.info("Bắt đầu quy trình ETL")
        
        if not self.extract():
            return False
        
        if not self.transform():
            return False
        
        if not self.load():
            return False
        
        logger.info("Quy trình ETL hoàn thành thành công!")
        return True

# Hàm main để chạy ETL
if __name__ == "__main__":
    # Cấu hình đường dẫn file CSV và kết nối database
    CSV_FILE_PATH = "products_data.csv"  # Thay đổi đường dẫn đến file CSV của bạn
    DB_CONFIG = {
        'dbname': 'your_database_name',
        'user': 'your_username',
        'password': 'your_password',
        'host': 'localhost',
        'port': '5432'
    }
    
    # Tạo chuỗi kết nối
    connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    
    # Khởi tạo và chạy ETL processor
    etl_processor = ETLProcessor(CSV_FILE_PATH, connection_string)
    success = etl_processor.run_etl()
    
    if success:
        print("ETL process completed successfully!")
    else:
        print("ETL process failed. Check logs for details.")