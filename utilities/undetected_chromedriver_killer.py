import time
import psutil
from custom_logger import get_logger


logger = get_logger("get_robots_txt_with_undetected_chromedriver")


def undetected_chromedriver_killer(driver):
    try:
        pid = driver.service.process.pid
        logger.info(f"PID: {pid}")

        driver.close()
        time.sleep(1)
        driver.quit()
        time.sleep(2)
        logger.info("Closed WebDriver")

        # Süreci kill et
        try:
            process = psutil.Process(pid)
            process.terminate()  # Süreci nazikçe sonlandırır
            process.wait(timeout=5)  # Sürecin kapanmasını bekler
        except psutil.NoSuchProcess:
            logger.info("Süreç zaten kapatılmış.")
        except psutil.AccessDenied:
            logger.info("Süreç kapatılamıyor; izinler reddedildi.")
        except psutil.TimeoutExpired:
            logger.info("Süreç kapanamadı; zaman aşımı gerçekleşti.")
        except Exception as ex:
            logger.exception(f"Genel hata: {ex}")
    except Exception as exception:
        logger.exception(f"AQ1 An error occurred while quitting the driver: {str(exception)}")