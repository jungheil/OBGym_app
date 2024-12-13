# coding: utf-8
# Copyright (c) 2024 Jungheil <jungheilai@gmail.com>
# OBGym is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import pytz
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from obgym_api import GymArea, GymCampus, GymFacility, OBGymAPI

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="OBGym API", description="OBGym 预约系统 API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量获取 Core API 配置
OBGYM_CORE_HOST = os.getenv("OBGYM_CORE_HOST", "localhost")
OBGYM_CORE_PORT = int(os.getenv("OBGYM_CORE_PORT", "16999"))

# 初始化 API 客户端
api = OBGymAPI(host=OBGYM_CORE_HOST, port=OBGYM_CORE_PORT)

CHINA_TIMEZONE = pytz.timezone("Asia/Shanghai")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """处理请求验证错误"""
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


class AccountResponse(BaseModel):
    account: str
    available: bool


class AccountRequest(BaseModel):
    account: str
    password: str


class JobPreview(BaseModel):
    job_id: str
    description: str
    created_at: str
    updated_at: str
    job_status: int
    job_level: int
    job_type: int


@app.get("/accounts", response_model=List[AccountResponse])
async def get_accounts():
    """取所有账户"""
    try:
        accounts = api.get_accounts()
        return [
            AccountResponse(account=account["account"], available=account["valid"])
            for account in accounts
        ]
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/accounts")
async def add_account(account_request: AccountRequest):
    """添加账户"""
    try:
        api.add_account(account_request.account, account_request.password)
        return {"message": "账户添加成功"}
    except Exception as e:
        logger.error(f"Error adding account: {e}")
        if isinstance(e, TypeError):
            raise HTTPException(status_code=400, detail="账号或密码格式错误")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/accounts/{account}")
async def delete_account(account: str):
    """删除账户"""
    try:
        api.remove_account(account)
        return {"message": "账户删除成功"}
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/campus/{account}", response_model=List[GymCampus])
async def get_campus(account: str):
    """取校区列表"""
    try:
        return api.get_campus(account)
    except Exception as e:
        logger.error(f"Error getting campus: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/facility/{account}", response_model=List[GymFacility])
async def get_facility(account: str, campus_code: str, campus_name: str):
    """获取场馆列表"""
    try:
        campus = GymCampus(code=campus_code, name=campus_name)
        return api.get_facility(campus, account)
    except Exception as e:
        logger.error(f"Error getting facility: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/area/{account}", response_model=List[GymArea])
async def get_area(
    account: str, facility_serviceid: str, facility_name: str, date: str
):
    """获取场地列表"""
    logging.debug(f"get_area: {account}, {facility_serviceid}, {facility_name}, {date}")
    try:
        facility = GymFacility(serviceid=facility_serviceid, name=facility_name)
        areas = api.get_area(facility, date, account)

        # 如果是当天的预约,过滤掉已经过期的时段
        if date == datetime.now(CHINA_TIMEZONE).strftime("%Y-%m-%d"):
            current_time = datetime.now(CHINA_TIMEZONE).time()
            filtered_areas = []

            for area_group in areas:
                # 假设时段格式为 "08:00-09:00"
                end_time_str = area_group.timeno.split("-")[1]
                end_time = (
                    datetime.strptime(end_time_str, "%H:%M")
                    .replace(tzinfo=CHINA_TIMEZONE)
                    .time()
                )

                if end_time > current_time:
                    filtered_areas.append(area_group)

            return filtered_areas

        return areas
    except Exception as e:
        logger.error(f"Error getting area: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/accounts/{account}/renew")
async def renew_account(account: str):
    """更新账户登录状态"""
    try:
        api.renew_account(account)
        return {"message": "账户更新成功"}
    except Exception as e:
        logger.error(f"Error renewing account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs", response_model=List[JobPreview])
async def get_all_jobs():
    """获取用户任务列表"""
    try:
        response = api.get_all_jobs()
        return response["all_jobs"]
    except Exception as e:
        logger.error(f"Error getting all jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class BookAreaRequest(BaseModel):
    sname: str
    sdate: str
    timeno: str
    serviceid: str
    areaid: str
    stockid: str
    account: str


@app.post("/area/book")
async def only_book_area(request: BookAreaRequest):
    """创建场地预约任务"""
    try:
        area = GymArea(
            sname=request.sname,
            sdate=request.sdate,
            timeno=request.timeno,
            serviceid=request.serviceid,
            areaid=request.areaid,
            stockid=request.stockid,
        )
        return api.only_book(area, request.account)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TaskTodo(BaseModel):
    task_id: str
    date: str


class TaskResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
    created_at: str


class JobInfoResponse(BaseModel):
    status: int
    job_level: int
    job_id: str
    description: str
    kwargs: Dict
    job_type: int
    result: List[TaskResult]
    failed_count: int
    created_at: str
    updated_at: str
    task_todo: Optional[TaskTodo] = None


@app.get("/jobs/{job_id}", response_model=JobInfoResponse)
async def get_job_info(job_id: str):
    """获取任务详细信息"""
    try:
        response = api.get_job_info(job_id)
        logging.info(response)
        return response
    except Exception as e:
        logger.error(f"Error getting job info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/jobs/{job_id}")
async def remove_job(job_id: str):
    """删除指定任务"""
    try:
        api.remove_job(job_id)
        return {"message": "任务删除成功"}
    except Exception as e:
        logger.error(f"Error removing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=16998)
